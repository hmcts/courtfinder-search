(function ($) {
  'use strict';

  if( $('#search-index-page').length > 0 ){

    // "Next" Button on /search/
    $('#search-index-page #start-button').click(function (){
        ga('send', 'event', 'search-index-page', 'next-button', 'Next button clicked to start');
    });

    // "Name or address" link on /search/
    $('#search-index-page a[href="/search/address"]').click(function (){
        ga('send', 'event', 'search-index-page', 'name-or-address-link', 'Name or address link clicked on start page');
    });

    // "A-Z list of all courts" link on /search/
    $('#search-index-page a[href="/courts/"]').click(function (){
        ga('send', 'event', 'search-index-page', 'a-z-courts-link', 'A-Z list of all courts link clicked on start page');
    });
  }

  if( $('#aol-page').length > 0 ){
    $('#aol-page form[action^="/search/"]').submit(function (e){
      var val = $('#aol-page label input:checked').val();
      var name = val.toLowerCase().replace(' ', '-');

      ga('send', 'event', 'aol-page', 'aol-' + name + '-selected', 'Area of Law selected: ' + val);
    });
  }
})(jQuery);
