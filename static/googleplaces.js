"use strict";

function initMap() {
    var inputs = document.getElementsByClassName('query');

    var options = {
        types: ['(cities)'],
        componentRestrictions: {country: 'us'}
    };

    var autocompletes = [];

    for (var i = 0; i < inputs.length; i++) {
        var autocomplete = new google.maps.places.Autocomplete(inputs[i], options);
        autocomplete.inputId = inputs[i].id;
        autocomplete.addListener('place_changed', fillIn);
        autocompletes.push(autocomplete);
    }

    function fillIn() {
        console.log(this.inputId);
        var place = this.getPlace();
        console.log(place.address_components[0].long_name);
    }
}

$('form').bind("keypress", function(e) {
  if (e.keyCode == 13) {
    e.preventDefault();
    return false;
  }
});