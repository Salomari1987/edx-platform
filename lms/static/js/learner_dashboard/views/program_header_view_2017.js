(function(define) {
    'use strict';

    define(['backbone',
            'jquery',
            'edx-ui-toolkit/js/utils/html-utils',
            'text!../../../templates/learner_dashboard/program_header_view_2017.underscore',
            'picturefill',
            'text!/static/images/programs/micromasters-program-details.svg',
            'text!/static/images/programs/xseries-program-details.svg',
            'text!/static/images/programs/professional-certificate-program-details.svg'
           ],
         function(Backbone, $, HtmlUtils, pageTpl, picturefill, MicroMastersLogo,
                  XSeriesLogo, ProfessionalCertificateLogo) {
             return Backbone.View.extend({
                 breakpoints: {
                     min: {
                         'medium': '768px',
                         'large': '1180px'
                     }
                 },

                 el: '.js-program-header',

                 tpl: HtmlUtils.template(pageTpl),

                 initialize: function() {
                     this.render();
                 },

                 getLogo: function() {
                    var logo,
                        type = this.model.get('programData').type;

                    if (type === 'MicroMasters'){
                        logo = MicroMastersLogo;
                    } else if (type === 'XSeries'){
                        logo = XSeriesLogo;
                    } else if (type === 'Professional Certificate') {
                        logo = ProfessionalCertificateLogo;
                    }
                    return logo;
                 },

                 render: function() {
                     var data = $.extend(this.model.toJSON(), {
                         breakpoints: this.breakpoints,
                         logo: this.getLogo()
                     });

                     if (this.model.get('programData')) {
                         HtmlUtils.setHtml(this.$el, this.tpl(data));
                         this.postRender();
                     }
                 },

                 postRender: function() {
                    // To resolve a bug in IE with picturefill reevaluate images
                     if (navigator.userAgent.indexOf('MSIE') !== -1 ||
                        navigator.appVersion.indexOf('Trident/') > 0) {
                        /* Microsoft Internet Explorer detected in. */
                         window.setTimeout(function() {
                             this.reEvaluatePicture();
                         }.bind(this), 100);
                     }
                 },

                 reEvaluatePicture: function() {
                     picturefill({
                         reevaluate: true
                     });
                 }
             });
         }
    );
}).call(this, define || RequireJS.define);
