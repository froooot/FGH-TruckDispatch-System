"use strict";
var placeIds = {"origin": "", "destination": ""}

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
        var place = this.getPlace();
        placeIds[this.inputId] = place.place_id;
        if (placeIds["origin"] && placeIds["destination"]) {
            var distance = new google.maps.DistanceMatrixService()
            distance.getDistanceMatrix({
                origins: [{'placeId': placeIds["origin"]}],
                destinations: [{'placeId': placeIds["destination"]}],
                travelMode: google.maps.TravelMode.DRIVING,
                unitSystem: google.maps.UnitSystem.IMPERIAL,
                avoidHighways: false,
                avoidTolls: false,
            }, callback);
        }

        function callback(response, status) {
            document.querySelector("#distance").value = response.rows[0].elements[0].distance.text
            document.querySelector("#duration").value = response.rows[0].elements[0].duration.text
        }
    }
}

$('form').bind("keypress", function (e) {
    if (e.keyCode == 13) {
        e.preventDefault();
        return false;
    }
});