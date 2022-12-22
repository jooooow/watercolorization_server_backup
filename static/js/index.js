function display_image(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            $('#input_image').attr('src', e.target.result);
        };

        reader.readAsDataURL(input.files[0]);
    }
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
        socket.on('dcenter', function (res) {
            console.log(res)
            console.log(res['sid'])
            var formData = new FormData($('#submit_form')[0]);
            formData.append("sid", res['sid'])
            console.log(formData)
            $.ajax({
                async: false,
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
                    console.log("socket.disconnect();");
                    socket.disconnect();
                }
            });
            
        });
        return false;
    })
});