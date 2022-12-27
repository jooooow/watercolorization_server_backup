function display_image(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            $('#input_image').attr('src', e.target.result);
        };
        reader.readAsDataURL(input.files[0]);
    }
}

$(window).on("load", function() {
    $('#submit_form').submit(function(event){
        var fileName = $(this).find("input[name=img_file]").val();
        if (fileName === '') 
        {
            alert('choose one file!');
            return;
        }

        namespace = '/dcenter';
        url = location.protocol + '//' + document.domain + ':' + location.port + namespace
        var socket = io.connect(url);

        socket.on('onconnected', function (res) {
            var sid = socket.id;
            //console.log(sid, "connected ", res)

            $('#return_msg').html('');
            $('#output_img_div').empty();
            $('#output_img_div').append('<img id="loading_img" class="mx-auto d-block">');
            $('#output_img_div').width($('#input_img_div').width());
            $('#loading_img').attr('src', '/static/img/uploading.gif');
            
            var formData = new FormData($('#submit_form')[0]);
            var uid = sid;
            var dot_pos = fileName.lastIndexOf('.')
            var slash_pos = fileName.lastIndexOf('\\')
            var img_name = fileName.substring(slash_pos + 1, dot_pos) + "_" + uid + "_result.png"

            if($("#bar").is(":visible") == true){
                var scale = $("#range_scale").val();
                var layers = $("#range_layers").val();
                var timeout = $("#range_timeout").val();
            }else{
                var scale = $("#select_scale option:selected" ).text();
                var layers = $("#select_layers option:selected" ).text();
                var timeout = $("#select_timeout option:selected" ).text();
            }

            formData.append('uid', uid);
            formData.append('scale', scale);
            formData.append('layers', layers);
            formData.append('timeout', timeout);

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
                    //console.log(sid, "disconnected", data)
                    socket.disconnect();
                    if(data['status'] == 200){
                        //console.log('output_img_path=',data['output_img_path']);
                        var output_img_path = data['output_img_path'];
                        $('#return_msg').html('finished in : ' + data['total_process_time'] + ' seconds');
                        $('#output_img_div').empty();
                        $('#output_img_div').append('<img id="output_img">');
                        $('#output_img_div').attr("style","width:auto");
                        $('#output_img_div').attr("style","height:auto");
                        $("#output_img").attr('src', output_img_path);
                    }else{
                        $('#return_msg').html('ERROR : ' + data['status']);
                        $('#loading_img').attr('src', '/static/img/error.svg');
                    }
                }
            });
        });
        
        socket.on('process_begin', function (res) {
            //console.log("process_begin");
            $('#loading_img').attr('src', '/static/img/loading.gif');
        });

        return false;
    })
});