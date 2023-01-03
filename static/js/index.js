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

$(window).on("load", function() {
    $("#advanced_setting").hide();
    $("#showhidden").click(function(){
        if($("#advanced_setting").is(":visible")){
            $("#advanced_setting").hide();
            $("#showhidden").css('rotate', '-90deg');
        }else{
            $("#advanced_setting").show();
            $("#showhidden").css('rotate', '0deg');
        }
    });

    $("#showhidden2").click(function(){
        if($("#settings2").is(":visible")){
            $("#settings2").hide();
            $("#showhidden2").css('rotate', '-90deg');
        }else{
            $("#settings2").show();
            $("#showhidden2").css('rotate', '0deg');
        }
    });

    $("#logo").dblclick(function(){
        window.open('/back'); 
    });


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

            if($("#bar").is(":visible") == true){
                var scale = $("#range_scale").val();
                var layers = $("#range_layers").val();
                var exposure = $("#range_exposure").val();
                var saturation = $("#range_saturation").val();
                var ETF = $("#range_ETF").val();
                var phase = $("#range_phase").val();
                var MPL = $("#range_MPL").val();
                var simscale = $("#range_simscale").val();
            }else{
                var scale = $("#select_scale option:selected" ).text();
                var layers = $("#select_layers option:selected" ).text();
                var exposure = $("#select_exposure option:selected").val();
                var saturation = $("#select_saturation option:selected").val();
                var ETF = $("#select_ETF option:selected" ).text();
                var phase = $("#select_phase option:selected" ).text();
                var MPL = $("#select_MPL option:selected" ).text();
                var simscale = $("#select_simscale option:selected" ).text();
            }
   
            formData.append('uid', uid);
            formData.append('scale', scale);
            formData.append('layers', layers);
            formData.append('exposure', exposure);
            formData.append('saturation', saturation);
            formData.append('ETF', ETF);
            formData.append('phase', phase);
            formData.append('max_pixel_len', MPL);
            formData.append('simscale', simscale);

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
                    socket.disconnect();
                    if(data['status'] == 200){
                        var output_img_path = data['output_img_path'];
                        var total_process_time = data['total_process_time'];
                        var compute_time = data['compute_time'];
                        $('#return_msg').html('finished in : ' + total_process_time + "s (" + compute_time + 's)');
                        $.ajax({
                            async: true,
                            url: output_img_path,
                            type: 'get',
                            beforeSend: function (xhr) {
                                xhr.overrideMimeType('text/plain; charset=x-user-defined');
                            },
                            success: function(result, textStatus, jqXHR) {
                                var binary = "";
                                var responseText = jqXHR.responseText;
                                var responseTextLen = responseText.length;

                                for ( i = 0; i < responseTextLen; i++ ) {
                                    binary += String.fromCharCode(responseText.charCodeAt(i) & 255)
                                }
                                $('#output_img_div').empty();
                                $('#output_img_div').append('<img id="output_img">');
                                $('#output_img_div').attr("style","width:auto;");
                                $("#output_img").attr('src', "data:image/png;base64,"+btoa(binary));
                            } 
                        });
                        $('#loading_img').attr('src', '/static/img/downloading.gif');
                    }else{
                        $('#return_msg').html('ERROR : ' + data['status']);
                        $('#loading_img').attr('src', '/static/img/error.svg');
                    }
                }
            });
        });
        
        socket.on('process_begin', function (res) {
            //console.log("process_begin");
            $('#loading_img').attr('src', '/static/img/processing.gif');
        });

        return false;
    })
});