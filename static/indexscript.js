
$("select").on("change", filter);
$("input").keypress(function(event){
    var keycode = (event.keyCode ? event.keyCode : event.key);
    if(keycode == '13'){
        filter();
    }
});
function filter() {
    let data = {
        "lot_id": $("#lot_id").val(),
        "pickup": new Date($("#pickup").val()).getTime()/1000,
        "delivery": new Date($("#delivery").val()).getTime()/1000,
        "origin": $("#origin").val(),
        "dh-o": $("#dh-o").val(),
        "destination": $("#destination").val(),
        "dh-d": $("#dh-d").val(),
        "contact": $("#contact").val(),
        "weight": $("#weight").val(),
        "rate": $("#rate").val(),
        "type": $("#truck_type").val()
    }
    window.location = generateUrl("/", data);
    console.log(data)

}
function generateUrl(url, params) {
    var i = 0, key;
    for (key in params) {
        if (i === 0) {
            url += "?";
        } else {
            url += "&";
        }
        url += key;
        url += '=';
        url += params[key];
        i++;
    }
    return url;
}
