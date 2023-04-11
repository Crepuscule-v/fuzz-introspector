from flask import render_template, Flask, url_for
from flask_socketio import SocketIO, Namespace
from threading import Lock
from utils import build_introspection_proj, update
import logging, sys, json
from PIL import Image

app = Flask(__name__)
socketio = SocketIO(app)
thread = None 
thread_lock = Lock()
logger = logging.getLogger(name=__name__)
introspector_target = None
data_dict = {}
nodes_idx = {}
edges_idx= {}

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

def init():
    '''
    Initializing 
    Parparing data_dict for client
    '''
    global introspector_target, data_dict, nodes_idx, edges_idx
    introspector_target, data_dict, nodes_idx, edges_idx = build_introspection_proj()
    return data_dict

def prepare_graph():
    """
    将 cg 和 cfg 对应的图片转存 static/img 文件夹下
    """
    img = Image.open("./example_1/work/fuzzer.ll.callgraph.png")
    img.save("./static/img/fuzzer.ll.callgraph.png")

class initNamespace(Namespace):
    def on_connect(self):
        logger.info("Connected to the page! \nPreparing for the data...")
        data_dict = init()
        prepare_graph()

        # 一个 Initital_data 的 event 
        self.emit("initial_data", data_dict)
        self.emit("send_cg_graph_url", {'cg_url': "http://127.0.0.1:5000/static/img/fuzzer.ll.callgraph.png"})
        logger.info("Data transfer finished")

class updateNamespace(Namespace):
    """
    启动一个线程，用于实时向客户端传输新的覆盖信息
    """
    def __init__(self, namespace=None):
        super().__init__(namespace)
        self.dataTransferThread = None
    
    def transferData(self):
        global introspector_target, data_dict
        while True:
            socketio.sleep(1.5)
            data_dict = update(introspector_target, data_dict, nodes_idx, edges_idx)
            self.emit("update_data", data_dict)
            logger.info("An updated data was transmitted to the client")
        
    def on_connect(self):
        if self.dataTransferThread is None:
            self.dataTransferThread = socketio.start_background_task(target = self.transferData)

socketio.on_namespace(initNamespace('/init'))
socketio.on_namespace(updateNamespace('/update'))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
