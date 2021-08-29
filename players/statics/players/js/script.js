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
});