(function ($) {
  'use strict';
    $(function () {
        if (!supportsInputAttribute('autofocus')) {
            $('[autofocus]').focus();
        }
    });
    // detect support for input attirbute
    function supportsInputAttribute (attr) {
        var input = document.createElement('input');
        return attr in input;
    }


  // Form focus styles
  // from https://github.com/alphagov/govuk_elements/blob/master/public/javascripts/application.js

  $('.block-label').each(function() {

    // Add focus
    $('.block-label input').focus(function() {
      $('label[for="' + this.id + '"]').addClass('add-focus');
      }).blur(function() {
      $('label').removeClass('add-focus');
    });
  });

})(jQuery);
