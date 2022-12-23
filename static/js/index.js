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
$(document).ready(function() {
    $('#submit_form').submit(function(event){
        var fileName = $(this).find("input[name=img_file]").val();
        console.log(fileName)
        if (fileName === '') 
        {
            alert('choose one file!');
            return;
        }

        namespace = '/dcenter';
        url = location.protocol + '//' + document.domain + ':' + location.port + namespace
        console.log("socket.connect(url);");
        var socket = io.connect(url);
        socket.on('onconnected', function (res) {
            console.log(res)
            console.log(res['sid'])
            var formData = new FormData($('#submit_form')[0]);
            formData.append("sid", res['sid'])
            console.log(formData)
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
                }
            });
            $('#output_img_div').empty();
            $('#output_img_div').append('<img id="loading_img">');
            $('#output_img_div').width($('#input_img_div').width());
            $('#loading_img').attr('src', '/static/img/loading.gif');
        });
        socket.on('recv_img', function (res) {
            console.log("recv_img")
            socket.disconnect();
            console.log("socket.disconnect();");
            img = res['image_data'];
            $('#output_img_div').empty();
            $('#output_img_div').append('<img id="output_img">');
            $('#output_img_div').attr("style","width:auto");
            $("#output_img").attr('src', "data:image/png;base64,"+b64(img));
        });
        socket.on('error', function (res) {
            console.log("error")
            console.log(res)
            $('#loading_img').attr('src', '/static/img/error.svg');
            socket.disconnect();
            console.log("socket.disconnect();");
        });
        return false;
    })
});