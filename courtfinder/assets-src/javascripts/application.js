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

})(jQuery);
