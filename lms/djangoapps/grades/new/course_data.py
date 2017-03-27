from lms.djangoapps.course_blocks.api import get_course_blocks
from xmodule.modulestore.django import modulestore
from ..transformer import GradesTransformer


class CourseData(object):
    """
    Houses course data and intelligently gets and caches the
    requested data as long as at least one is provided upon
    initialization.
    """
    def __init__(self, user, course=None, collected_block_structure=None, course_structure=None, course_key=None):
        self.user = user
        self._course = course
        self._collected_block_structure = collected_block_structure
        self._structure = course_structure
        self._course_key = course_key
        self._location = None

    @property
    def course_key(self):
        if not self._course_key:
            if self._course:
                self._course_key = self._course.id
            else:
                structure = self._structure or self._collected_block_structure
                self._course_key = structure.root_block_usage_key.course_key
        return self._course_key

    @property
    def location(self):
        if not self._location:
            structure = self._structure or self._collected_block_structure
            if structure:
                self._location = structure.root_block_usage_key
            elif self._course:
                self._location = self._course.location
            else:
                self._location = modulestore().make_course_usage_key(self._course_key)
        return self._location

    @property
    def grading_policy_hash(self):
        structure = self._structure or self._collected_block_structure
        if structure:
            return structure.get_transformer_block_field(
                structure.root_block_usage_key,
                GradesTransformer,
                'grading_policy_hash',
            )
        else:
            course = self._course or modulestore().get_course(self._course_key)
            return GradesTransformer.grading_policy_hash(course)

    @property
    def structure(self):
        if not self._structure:
            self._structure = get_course_blocks(
                self.user,
                self.location,
                collected_block_structure=self._collected_block_structure,
            )
        return self._structure

    @property
    def course(self):
        if not self._course:
            self._course = modulestore().get_course(self.course_key)
        return self._course
