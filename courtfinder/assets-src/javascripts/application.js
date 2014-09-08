$(function() {
  'use strict';

  $('#aols').css('display', $('#aol-one').prop('checked') ? 'block' : 'none');
  $('#aols, #aol-one-label').addClass('js');

  $('#aol-one-label').css('display', 'block');
  $('#aol-hint').css('display', 'block');
  $('.aol-label').css('margin-left', '1em');

  $('#aol-0').on('change', function() { $('#aols').css('display', 'none'); });
  $('#aol-one').on('change', function() { $('#aols').css('display', 'block'); });
});
