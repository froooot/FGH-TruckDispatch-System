$("#changephotobutton").change(function () {
    loadImageFile()
});

var fileReader = new FileReader();
var filterType = /^(?:image\/bmp|image\/cis\-cod|image\/gif|image\/ief|image\/jpeg|image\/jpeg|image\/jpeg|image\/pipeg|image\/png|image\/svg\+xml|image\/tiff|image\/x\-cmu\-raster|image\/x\-cmx|image\/x\-icon|image\/x\-portable\-anymap|image\/x\-portable\-bitmap|image\/x\-portable\-graymap|image\/x\-portable\-pixmap|image\/x\-rgb|image\/x\-xbitmap|image\/x\-xpixmap|image\/x\-xwindowdump)$/i;

fileReader.onload = function (event) {
    var image = new Image();

    image.onload = function () {
        document.getElementById("changephotobutton").src = image.src;
        var canvas = document.createElement("canvas");
        var context = canvas.getContext("2d");
        canvas.width = image.width / (image.height / 300);
        canvas.height = 300;
        context.drawImage(image,
            0,
            0,
            image.width,
            image.height,
            0,
            0,
            canvas.width,
            canvas.height
        );

        document.getElementById("profilephoto").src = canvas.toDataURL();

    }
    image.src = event.target.result;
};

var loadImageFile = function () {
    var uploadImage = document.getElementById("changephotobutton");

    //check and retuns the length of uploded file.
    if (uploadImage.files.length === 0) {
        return;
    }

    //Is Used for validate a valid file.
    var uploadFile = document.getElementById("changephotobutton").files[0];
    if (!filterType.test(uploadFile.type)) {
        alert("Please select a valid image.");
        return;
    }

    fileReader.readAsDataURL(uploadFile);
}

$("#savedata").click(function () {
    userdata = {
        "firstname": $("#firstname").val(),
        "lastname": $("#lastname").val(),
        "email": $("#email").val(),
        "phone": $("#phone").val(),
        "bio": $("#bio").val(),
        "photo": $("#profilephoto").attr("src")
    };
    $.post('/profileedit',
        userdata, // data to be submit
        window.location.replace("/profile")
    );
})