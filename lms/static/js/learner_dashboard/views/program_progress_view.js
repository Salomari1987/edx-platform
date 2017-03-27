(function(define) {
    'use strict';

    define(['backbone',
            'jquery',
            'underscore',
            'gettext',
            'text!../../../templates/learner_dashboard/program_progress_view.underscore',
            'text!../../../templates/learner_dashboard/program_progress_segment.underscore'
           ],
        function(
            Backbone,
            $,
            _,
            gettext,
            programProgressTpl,
            progressSegmentTpl
        ) {
            return Backbone.View.extend({
                x: 22,
                y: this.x,
                radius: 16,
                degrees: 180,
                strokeWidth: 1.4,

                viewTpl: _.template(programProgressTpl),
                segmentTpl: _.template(progressSegmentTpl),

                initialize: function() {
                    var progress;

                    // Temp. for development
                    this.model.set({
                        progress: {
                            completed: 3,
                            in_progress: 0,
                            not_started: 3
                        }
                    });
                    progress = this.model.get('progress');

                    this.model.set({
                        totalCourses: progress.completed + progress.in_progress + progress.not_started
                    });

                    this.render();
                },

                render: function() {
                    var data = $.extend({}, this.model.toJSON(), {
                        progress: this.getProgressSegments(),
                        x: this.x,
                        y: this.y,
                        radius: this.radius,
                        strokeWidth: this.strokeWidth
                    });

                    this.$el.html(this.viewTpl(data));
                },

                getDegreeIncrement: function(total) {
                    return 360 / total;
                },

                getOffset: function(total) {
                    return 100 - ((1 / total) * 100);
                },

                getProgressSegments: function() {
                    var progressHTML = [],
                        total = this.model.get('total'),
                        degreeInc = this.getDegreeIncrement(total),
                        data = {
                            dashArray: 2 * Math.PI * this.radius,
                            degrees: this.degrees,
                            offset: this.getOffset(total), //plus gap:  + 1.4;
                            x: this.x,
                            y: this.y,
                            radius: this.radius,
                            strokeWidth: this.strokeWidth
                        },
                        i;

                    for (i = 0; i < total; i++) {
                        progressHTML.push(this.segmentTpl($.extend({}, data, {
                            classList: (i > this.model.get('progress').complete) ? 'incomplete' : 'complete',
                            degrees: data.degrees + (i * degreeInc)
                        })));
                    }

                    return progressHTML.join('');
                }
             });
         }
    );
}).call(this, define || RequireJS.define);
