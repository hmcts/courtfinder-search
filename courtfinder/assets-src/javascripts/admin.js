(function ($) {
  'use strict';

  /* forms */
  tinymce.init({
    selector: '.rich-editor:enabled',
    width: 774,
    plugins : 'autolink link paste',
    menubar: '',
    toolbar: 'link bold italic underline',
    paste_as_text: true,
    statusbar: false,
  });

  setTimeout(function(){
    $('.messages').fadeTo('slow', 0.5);
  }, 5000);


  /* court list */
  $('#closed-court-toggle').change(function(){
    $('tr.closed-court').toggleClass('hidden');
  })

  //add case insensitive contains function
  jQuery.expr[":"].icontains = jQuery.expr.createPseudo(function (arg) {
    return function (elem) {
      return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
  });

  $('#court-search-box').on('input',function(e){
    var search = $(this).val();
    $('#closed-court-toggle').prop('checked', true).prop('disabled', search);
    $('#court-list tr:not(:first-child)').addClass('hidden');
    $("#court-list td:first-child:icontains('" + search + "')").parent().removeClass('hidden');
  })

  /* password generator */
  $('#generate-password').click(function(){
    var button = $(this);
    var password = button.data('pass');
    $('#id_password1').val(password).attr('type', 'text');
    $('#id_password2').val(password).attr('type', 'text');
    button.hide();
  });

  /* reordering js */
  $("#sortable").sortable({
    axis: "y"
  });
  $("#sortable").disableSelection();
  $("#sortable").on("sortstop", function(event, ui) {
    var sortedIDs = $("#sortable").sortable("toArray");
    var ordering = JSON.stringify(sortedIDs);
    $("#new_sort_order").val(ordering);
  });

  $('.orderable').on('click', '.destroy .remove', function(e) {
    e.preventDefault();

    $(this).closest('.destroy').siblings('div').hide();
    $(this).hide().siblings('.undo').show().siblings('.undo_msg').show();
    $(this).parent('div').siblings('p').filter(":not(:has(input[name*='DELETE']))").hide();
    $(this).parent('div').siblings('p').filter(":has(input[name*='DELETE'])").children('input').prop('checked', true);
  });

  $('.orderable').on('click', '.destroy .undo', function(e) {
    e.preventDefault();

    $(this).closest('.destroy').siblings('div').not('[class$="sort"]').show();
    $(this).hide().siblings('.remove').show().siblings('.undo_msg').hide();
    $(this).parent('div').siblings('p').filter(":not(:has(input[name*='DELETE']))").show();
    $(this).parent('div').siblings('p').filter(":has(input[name*='DELETE'])").children('input').prop('checked', false);
  });

  /* postcode management */
  $('input[name=action]').change(function(){
    $('#move-button')
      .attr('value', this.value == 'move' ? 'Move postcodes' : 'Delete - this operation is irreversible, are you sure?')
      .toggleClass('button', this.value == 'move')
      .show();
  });
  $('input[name=action]:checked').trigger('change');

})(jQuery);