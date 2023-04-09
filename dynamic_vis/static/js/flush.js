function onload() {
    // 页面全部加载完毕之后调用 ready 函数
    $(document).ready(function() {
        namespace='/test'
        var socket = io.connect('ws://127.0.0.1:5000/test');
        
        socket.on('server_response', function(res) {
            var msg = res.data;
            console.log(msg);
            document.getElementById("random").innerHTML = '<p>'+msg+'</p>';
        }); 
   	});
}

