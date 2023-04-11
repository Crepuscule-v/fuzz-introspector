function init() {
    var init_namespace = "init";
    var update_namespace = "update";
    const initSocket = io.connect('ws://127.0.0.1:5000/' + init_namespace);

    initSocket.on('connect', () => {
        console.log('Connected to init namespace');
    });

    // 接收服务器传来的初始化 data_dict, 绘制初始力导向图
    initSocket.on('initial_data', (data_dict) => {
        console.log("Recieved initial data, Preparing for drawing FDG")
        console.log(data_dict)
        initFDGraph(data_dict)
    })

    initSocket.on("send_cg_graph_url", (data_dict) => {
        console.log("Received cg graph")
        set_cg_graph(data_dict.cg_url)
    })

    // 初始化结束之后, 创建与 update namespace 的连接，启动后台线程
    const updateSocket = io.connect("ws://127.0.0.1:5000/" + update_namespace);
    updateSocket.on('connect', () => {
        console.log("Connected to update namespace")
    })

    // 利用每次接收到的新的数据, 更新力导向图
    updateSocket.on("update_data", (data_dict) => {
        console.log("received new data")
        updateFDGraph(data_dict)
    })
}

function set_cg_graph(url) {
    const container = document.getElementById("call_graph");
    const img = document.createElement("img");
    img.src = url;

    img.addEventListener("load", function() {
        const containerRatio = container.clientWidth / container.clientHeight;
        const imgRatio = img.width / img.height;

        if (containerRatio < imgRatio) {
        img.style.width = "100%";
        img.style.height = "auto";
        } else {
        img.style.width = "auto";
        img.style.height = "100%";
        }
        img.style.display = "inline-block";
    });
    container.appendChild(img);
}