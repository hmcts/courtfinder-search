(function ($) {
  'use strict';

  /* forms */
  tinymce.init({
    selector: '.rich-editor',
    width: 784,
    plugins : 'autolink link',
    menubar: '',
    toolbar: 'undo redo | bold italic underline strikethrough | link | removeformat',
    statusbar: false,
  });

  setTimeout(function(){
    $('.form-feedback').fadeOut(1000);
  }, 3000);


  /* court list */
  $('#closed-court-toggle').click(function(){
    $('.closed-court').toggleClass('hidden');
  })

  jQuery.expr[":"].icontains = jQuery.expr.createPseudo(function (arg) {
    return function (elem) {
      return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
  });

  $('#court-search-box').on('input',function(e){
    $('#closed-court-toggle').prop('checked', true);
    $('#court-list tr').addClass('hidden');
    $("#court-list td:icontains('" + $(this).val() + "')").parent().removeClass('hidden');
  })

})(jQuery);
