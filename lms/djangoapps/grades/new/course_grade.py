"""
CourseGrade Class
"""
from abc import abstractmethod
from collections import defaultdict, OrderedDict
from django.conf import settings
from lazy import lazy
from logging import getLogger

from xmodule import block_metadata_utils
from .subsection_grade_factory import SubsectionGradeFactory
from .subsection_grade import ZeroSubsectionGrade


log = getLogger(__name__)


class CourseGradeBase(object):
    """
    Base class for Course Grades.
    """
    def __init__(self, user, course_data, percent=0, letter_grade=None, passed=False):
        self.user = user
        self.course_data = course_data

        self.percent = percent
        self.letter_grade = letter_grade
        self.passed = passed

    def attempted(self):
        """
        Returns whether at least one problem was attempted
        by the user in the course.
        """
        return False

    @lazy
    def graded_subsections_by_format(self):
        """
        Returns grades for the subsections in the course in
        a dict keyed by subsection format types.
        """
        subsections_by_format = defaultdict(OrderedDict)
        for chapter in self.chapter_grades.itervalues():
            for subsection_grade in chapter['sections']:
                if subsection_grade.graded:
                    graded_total = subsection_grade.graded_total
                    if graded_total.possible > 0:
                        subsections_by_format[subsection_grade.format][subsection_grade.location] = subsection_grade
        return subsections_by_format

    @lazy
    def chapter_grades(self):
        """
        Returns a dictionary of dictionaries.
        The primary dictionary is keyed by the chapter's usage_key.
        The secondary dictionary contains the chapter's
        subsection grades, display name, and url name.
        """
        course_structure = self.course_data.structure
        return {
            chapter_key: self._get_chapter_grade_info(course_structure[chapter_key], course_structure)
            for chapter_key in course_structure.get_children(self.course_data.location)
        }

    @lazy
    def locations_to_scores(self):
        """
        Returns a dict of problem scores keyed by their locations.
        """
        locations_to_scores = {}
        for chapter in self.chapter_grades.itervalues():
            for subsection_grade in chapter['sections']:
                locations_to_scores.update(subsection_grade.locations_to_scores)
        return locations_to_scores

    @lazy
    def grader_result(self):
        """
        Returns the result from the course grader.
        """
        course = self.course_data.course
        course.set_grading_policy(course.grading_policy)
        return course.grader.grade(
            self.graded_subsections_by_format,
            generate_random_scores=settings.GENERATE_PROFILE_SCORES,
        )

    @property
    def summary(self):
        """
        Returns the grade summary as calculated by the course's grader.
        DEPRECATED: To be removed as part of TNL-5291.
        """
        grade_summary = self.grader_result
        grade_summary['percent'] = self.percent
        grade_summary['grade'] = self.letter_grade
        return grade_summary

    def _get_chapter_grade_info(self, chapter, course_structure):
        """
        Helper that returns a dictionary of chapter grade information.
        """
        chapter_subsection_grades = self._get_subsection_grades(course_structure, chapter.location)
        return {
            'display_name': block_metadata_utils.display_name_with_default_escaped(chapter),
            'url_name': block_metadata_utils.url_name_for_block(chapter),
            'sections': chapter_subsection_grades,
        }

    def _get_subsection_grades(self, course_structure, chapter_key):
        """
        Returns a list of subsection grades for the given chapter.
        """
        return [
            self._get_subsection_grade(course_structure[subsection_key])
            for subsection_key in course_structure.get_children(chapter_key)
        ]

    @abstractmethod
    def _get_subsection_grade(self, subsection):
        """
        Abstract method to be implemented by subclasses for returning
        the grade of the given subsection.
        """
        raise NotImplementedError


class ZeroCourseGrade(CourseGradeBase):
    """
    Course Grade class for Zero-value grades when no problems were
    attempted in the course.
    """
    def __init__(self, user, course_data):
        super(ZeroCourseGrade, self).__init__(user, course_data)

    def _get_subsection_grade(self, subsection):
        return ZeroSubsectionGrade(subsection, self.course_data)


class CourseGrade(CourseGradeBase):
    """
    Course Grade class when grades are updated or read from storage.
    """
    def __init__(self, user, course_data, *args, **kwargs):
        super(CourseGrade, self).__init__(user, course_data, *args, **kwargs)
        self._subsection_grade_factory = SubsectionGradeFactory(user, course_data=course_data)

    def update(self):
        """
        Updates the grade for the course.
        """
        grade_cutoffs = self.course_data.course.grade_cutoffs
        self.percent = self._compute_percent(self.grader_result)
        self.letter_grade = self._compute_letter_grade(grade_cutoffs, self.percent)
        self.passed = self._compute_passed(grade_cutoffs, self.percent)

        subs_total = sum(len(chapter['sections']) for chapter in self.chapter_grades.itervalues())
        subs_created = len(self._subsection_grade_factory._unsaved_subsection_grades)  # pylint: disable=protected-access
        subs_read = subs_total - subs_created
        self._log_event(
            log.warning,
            u"update, subsections read/created/total: {}/{}/{}".format(subs_read, subs_created, subs_total)
        )

    @lazy
    def attempted(self):
        """
        Returns whether any of the subsections in this course
        have been attempted by the student.
        """
        for chapter in self.chapter_grades.itervalues():
            for subsection_grade in chapter['sections']:
                if subsection_grade.attempted:
                    return True
        return False

    def _get_subsection_grade(self, subsection):
        # Pass read_only here so the subsection grades can be persisted in bulk at the end.
        return self._subsection_grade_factory.create(subsection, read_only=True)

    @staticmethod
    def _compute_percent(grader_result):
        """
        Computes and returns the grade percentage from the given
        result from the grader.
        """
        return round(grader_result['percent'] * 100 + 0.05) / 100

    @staticmethod
    def _compute_letter_grade(grade_cutoffs, percent):
        """
        Computes and returns the course letter grade given the
        inputs, as defined in the grading_policy (e.g. 'A' 'B' 'C')
        or None if not passed.
        """
        letter_grade = None

        # Possible grades, sorted in descending order of score
        descending_grades = sorted(grade_cutoffs, key=lambda x: grade_cutoffs[x], reverse=True)
        for possible_grade in descending_grades:
            if percent >= grade_cutoffs[possible_grade]:
                letter_grade = possible_grade
                break

        return letter_grade

    @staticmethod
    def _compute_passed(grade_cutoffs, percent):
        """
        Computes and returns whether the given percent value
        is a passing grade according to the given grade cutoffs.
        """
        nonzero_cutoffs = [cutoff for cutoff in grade_cutoffs.values() if cutoff > 0]
        success_cutoff = min(nonzero_cutoffs) if nonzero_cutoffs else None
        return success_cutoff and percent >= success_cutoff

    def _log_event(self, log_func, log_statement):
        """
        Logs the given statement, for this instance.
        """
        log_func(u"Persistent Grades: CourseGrade.{0}, course: {1}, user: {2}".format(
            log_statement,
            self.course_data.course_key,
            self.user.id
        ))
