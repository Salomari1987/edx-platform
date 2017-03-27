define([
    'backbone',
    'jquery',
    'js/learner_dashboard/views/program_progress_view'
], function(Backbone, $, ProgramProgressView) {
    'use strict';

    describe('Program Progress View', function() {
        var view = null,
            context = {
                urls: {
                    program_listing_url: '/dashboard/programs'
                },
                programData: {
                    uuid: 'a87e5eac-3c93-45a1-a8e1-4c79ca8401c8',
                    title: 'Food Security and Sustainability',
                    subtitle: 'Learn how to feed all people in the world in a sustainable way.',
                    type: 'XSeries',
                    detail_url: 'https://www.edx.org/foo/bar',
                    banner_image: {
                        medium: {
                            height: 242,
                            width: 726,
                            url: 'https://example.com/a87e5eac-3c93-45a1-a8e1-4c79ca8401c8.medium.jpg'
                        },
                        'x-small': {
                            height: 116,
                            width: 348,
                            url: 'https://example.com/a87e5eac-3c93-45a1-a8e1-4c79ca8401c8.x-small.jpg'
                        },
                        small: {
                            height: 145,
                            width: 435,
                            url: 'https://example.com/a87e5eac-3c93-45a1-a8e1-4c79ca8401c8.small.jpg'
                        },
                        large: {
                            height: 480,
                            width: 1440,
                            url: 'https://example.com/a87e5eac-3c93-45a1-a8e1-4c79ca8401c8.large.jpg'
                        }
                    },
                    authoring_organizations: [
                        {
                            uuid: '0c6e5fa2-96e8-40b2-9ebe-c8b0df2a3b22',
                            key: 'WageningenX',
                            name: 'Wageningen University & Research',
                            certificate_logo_image_url: 'https://example.com/org-certificate-logo.jpg',
                            logo_image_url: 'https://example.com/org-logo.jpg'
                        }
                    ]
                },
                progress: {
                    completed: 3,
                    in_progress: 1,
                    not_started: 2
                }
            },
            testCircle,
            testText,
            updateProgress;

        testCircle = function(data) {
            var $circle = view.$('.progress-circle'),
                progress = data.progress;

            expect($circle.find('.complete').length).toEqual(progress.completed);
            expect($circle.find('.incomplete').length).toEqual(progress.in_progress + progress.not_started);
        };

        testText = function(data) {
            var $numbers = view.$('.numbers');

            expect(view.$('.progress-heading').html()).toEqual('XSeries Progress');
            expect($numbers.find('.complete').html()).toEqual(data.progress.completed);
            expect($numbers.find('.total').html()).toEqual(data.progress.completed + data.progress.in_progress + data.progress.not_started);
        };

        updateProgress = function(x, y, z) {
            return $.extend({}, context, {
                progress: {
                    completed: x,
                    in_progress: y,
                    not_started: z
                }
            });
        }

        beforeEach(function() {
            setFixtures('<div class="js-program-header"></div>');
            view = new ProgramProgressView({
                model: new Backbone.Model(context)
            });
            view.render();
        });

        afterEach(function() {
            view.remove();
        });

        it('should exist', function() {
            expect(view).toBeDefined();
        });

        it('should render the progress circle based on the passed in model', function() {
            testCircle(context);
        });

        it('should render the progress text based on the passed in model', function() {
            testText(context);
        });

        it('should render the progress text with only completed courses', function() {
            var data = updateProgress(5, 0, 0);

            view.model.set(data);
            view.render();
            testCircle(data);
            testText(data);
        });

        it('should render the progress text with only in progress courses', function() {
            var data = updateProgress(0, 4, 0);

            view.model.set(data);
            view.render();
            testCircle(data);
            testText(data);
        });

        it('should render the progress circle with only not started courses', function() {
            var data = updateProgress(0, 0, 5);

            view.model.set(data);
            view.render();
            testCircle(data);
            testText(data);
        });

        it('should render the progress text with no completed courses', function() {
            var data = updateProgress(0, 2, 3);

            view.model.set(data);
            view.render();
            testCircle(data);
            testText(data);
        });

        it('should render the progress text with no in progress courses', function() {
            var data = updateProgress(2, 0, 7);

            view.model.set(data);
            view.render();
            testCircle(data);
            testText(data);
        });
        
        it('should render the progress text with no not started courses', function() {
            var data = updateProgress(2, 4, 0);

            view.model.set(data);
            view.render();
            testCircle(data);
            testText(data);
        });
    });
}
);
