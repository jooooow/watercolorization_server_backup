function display_image(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#input_image').attr('src', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
    }
}
function b64(e){
    var t="";
    var n=new Uint8Array(e);
    var r=n.byteLength;
    for(var i=0;i<r;i++)
    {
        t+=String.fromCharCode(n[i])
    }
    return window.btoa(t)
}

function S4() {
    return (((1+Math.random())*0x10000)|0).toString(16).substring(1);
 }
 function guid() {
    return (S4()+S4()+"-"+S4()+"-"+S4()+"-"+S4()+"-"+S4()+S4()+S4());
 }

$(document).ready(function() {
    $('#submit_form').submit(function(event){
        var fileName = $(this).find("input[name=img_file]").val();
        if (fileName === '') 
        {
            alert('choose one file!');
            return;
        }

        $('#output_img_div').empty();
        $('#output_img_div').append('<img id="loading_img">');
        $('#output_img_div').width($('#input_img_div').width());
        $('#loading_img').attr('src', '/static/img/loading.gif');
        
        var formData = new FormData($('#submit_form')[0]);
        var uid = guid();
        var dot_pos = fileName.lastIndexOf('.')
        var slash_pos = fileName.lastIndexOf('\\')
        var img_name = fileName.substring(slash_pos + 1, dot_pos) + "_" + uid + "_result.png"

        formData.append('uid', uid);
        $.ajax({
            async: true,
            type: "POST",
            url: "/upload",
            data: formData,
            dataType: "JSON",
            mimeType: "multipart/form-data",
            contentType: false,
            cache: false,
            processData: false,
            success: function (data) {
                console.log(data)
                if(data == 200){
                    $('#output_img_div').empty();
                    $('#output_img_div').append('<img id="output_img">');
                    $('#output_img_div').attr("style","width:auto");
                    $('#output_img_div').attr("style","height:auto");
                    $("#output_img").attr('src', "/static/outputs/" + img_name);
                }else{
                    $('#loading_img').attr('src', '/static/img/error.svg');
                }
            }
        });
        

        return false;
    })
});