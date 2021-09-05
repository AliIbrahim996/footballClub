/**
 * Jquery function to open a new image and show a preview
 */

$(".imgAdd").click(function () {
    $(this).closest(".row").find('.imgAdd').before('<div class="col-sm-2 imgUp"><div class="imagePreview"></div><label class="btn btn-primary">Upload<input type="file" class="uploadFile img" value="Upload Photo" css="width:0px;height:0px;overflow:hidden;"></label><i class="fa fa-times del"></i></div>');
});
$(document).on("click", "i.del", function () {
    $(this).parent().remove();
});
$(function () {
    $(document).on("change", ".uploadFile", function () {
        let uploadFile = $(this);
        let files = !!this.files ? this.files : [];
        if (!files.length || !window.FileReader) return; // no file selected, or no FileReader support

        if (/^image/.test(files[0].type)) { // only image file
            let reader = new FileReader(); // instance of the FileReader
            reader.readAsDataURL(files[0]); // read the local file

            reader.onloadend = function () { // set image data as background of div
                uploadFile.closest(".imgUp").find('.imagePreview').css("background-image", "url(" + this.result + ")");
            }
        }

    });
});


/**
 * Jquery function to filter get request sent from search page
 */

$(document).ready(function () {
    $("#search_form").submit(function () {
        if ($("#search_box").val() === "") {
            $("#search_box").remove();
        }
        if ($("#manager").val() === "" || $("#manager").val() === "--------") {
            $("#manager").remove();
        }
        if ($("#start_date").val() === "" || $("#end_date").val() === "") {
            $("#start_date").remove();
            $("#end_date").remove();
        }
    });

    let image_file = "";
    let can = document.createElement("canvas");
    can.id = "screenShoot";
    can.setAttribute("style", "position: absolute;");
    can.setAttribute("hidden", "");
    let take_screen_shoot = async () => {
        let find_can = document.getElementById("screenShoot")
        if (find_can == null)
            document.getElementById("form_container").appendChild(can);
        let stream = await navigator.mediaDevices.getDisplayMedia({displaySurface: 'active-window'});
        let track = stream.getVideoTracks()[0];
        let image = new ImageCapture(track);
        let bitmap = await image.grabFrame();
        track.stop();
        let canvas = document.getElementById("screenShoot");
        canvas.width = bitmap.width;
        canvas.height = bitmap.height;
        let context = canvas.getContext('2d');
        //drawImage(video, domX, domY, domWidth, domHeight, 0, 0, domWidth, domHeight);
        context.drawImage(bitmap,
            50, 50,  // Start at pixels from the left and the top of the image (crop),
            bitmap.width - 100, bitmap.height - 200,   // Get a  (w * h) area from the source image (crop),
            0, 0,
            bitmap.width, bitmap.height //scaling
        );
        let img = canvas.toDataURL();
        let result = await fetch(img);
        let buffer = await result.arrayBuffer();
        let name = document.getElementsByName("created_by").item(0).value;
        let date = document.getElementsByName("created_at").item(0).value;
        /*let img_file = canvas.toDataURL().replace("data:image/png;base64,", "");
        downloadBase64File("image/png;base64", img_file, name + "_" + date);*/
        image_file = new File([buffer], name + "_" + date + ".png", {type: 'image/png'});
    };
    $("#plan_form").submit(function (event) {
        // Prevent the default form submit
        event.preventDefault();
        let form = this;
        let formData = new FormData(form);
        take_screen_shoot().then(function () {
            formData.append('image', image_file)
            $.ajax({
                url: form.action,
                type: form.method,
                data: formData,
                processData: false,
                contentType: false,
                cache: false,
                enctype: 'multipart/form-data',
                success: [function (response) {
                    form.reset();
                    createConfirmDiv(response['message']);
                }],
                error: [function (response) {
                    alert("failed to submit form!");
                }]
            });
        })
    });
});

function createConfirmDiv(message) {
    $("#form_container")
        .append('<div id="alert" class="alert alert-success " role="alert" style="width: fit-content">' + message + '</div>' +
            '<script type="text/javascript">'
            + 'setTimeout(function () {' + '$("#alert").alert("close");' + '}, 3000);' + '</script>')
}

function downloadBase64File(contentType, base64Data, fileName) {
    const linkSource = `data:${contentType};base64,${base64Data}`;
    const downloadLink = document.createElement("a");
    downloadLink.href = linkSource;
    downloadLink.download = fileName;
    downloadLink.click();
}