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
    $('#aol-page form[action^="/search/"]').submit(function (){
      var val = $('#aol-page label input:checked').val();
      var name = val.toLowerCase().replace(' ', '-');

      ga('send', 'event', 'aol-page', 'aol-' + name + '-selected', 'Area of Law selected: ' + val);
    });
  }

  if( $('#spoe-page').length > 0 ){
    $('#spoe-page form[action^="/search"]').submit(function (){
      var selected = $('#spoe-page form label input:checked').val();
      var label = selected == 'start' ? "Starting a new claim selected" : "Already in contact selected";

      ga('send', 'event', 'spoe-page', 'spoe-' + selected + 'selected', label);
    });
  }

  if( $('#postcode-page').length > 0 ){
    $('#postcode-page #housing-possession-online-link').click(function (){
      ga('send', 'event', 'postcode-page', 'housing-possession-online-link-clicked', 'Housing possession online link clicked');
    });

    $('#postcode-page #money-claims-online-link').click(function (){
      ga('send', 'event', 'postcode-page', 'money-claims-online-link-clicked', 'Money claims online link clicked');
    });
  }

  if( $('#search-results-page').length > 0 ){
    $('#search-results-page .court-map a').click(function (){
      ga('send', 'event', 'search-results-page', 'map-link-clicked', 'A map link clicked on search results');
    });
  }
})(jQuery);
