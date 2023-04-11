import graphviz
import networkx as nx 
import pydot 
import cxxfilt
import constant_val
from typing import List, Dict, Any, Tuple

def demangle_cpp_func(funcname: str) -> str:
    try:
        demangled: str = cxxfilt.demangle(funcname)
        return demangled
    except Exception:
        return funcname

def parse_dot_file_to_networkx(file_path):
    with open(file_path, 'r') as file:
        dot_content = file.read()
    dot_graph = graphviz.Source(dot_content)
    pydot_graph = pydot.graph_from_dot_data(dot_graph.source)[0]
    return nx.drawing.nx_pydot.from_pydot(pydot_graph)

def process_cg() -> Tuple[Dict[str, List[Any]], Dict[Any, Any], Dict[Any, Any]]:
    file_name = constant_val.CALLGRAPH_FILE_NAME
    nx_graph = parse_dot_file_to_networkx("./example_1/work/" + file_name)
    return process(nx_graph)

def process(nx_graph) -> Tuple[Dict[str, List[Any]], Dict[Any, Any], Dict[Any, Any]]:
    """
    对 call graph 进行处理
    返回值：
        [Dict, Dict, Dict]
            - {"nodes_list" : [], "edges_list" : []}
            - {"function_name", [node_id, idx]}    
            - {("src_func_name", "dst_func_name"), idx}      
    """
    data_dict = {}
    nodes_list = []
    edges_list = []
    nodes_idx = {}
    edges_idx = {}
    tmp_idx = {}           # 临时用于 node -> idx 的索引
    idx = 0
    for node, attrs in nx_graph.nodes(data=True):
        node_dict = {}
        node_dict["id"] = node
        
        for key in attrs:
            if key == "label":
                node_dict["function_name"] = demangle_cpp_func(attrs[key][2:-2])
                node_dict["hit_count"] = 0
                node_dict["function_source_file"] = ""
                node_dict["arg_count"] = ""
                node_dict["bb_count"] = ""
                node_dict["i_count"] = ""
                node_dict["edge_count"] = ""
                node_dict["function_linenumber"] = ""
                node_dict["color"] = "#99CCCC"
        
        nodes_list.append(node_dict)
        nodes_idx[node_dict["function_name"]] = [idx, node]
        tmp_idx[node] = idx
        idx += 1
    
    idx = 0
    for src, dst, attrs in nx_graph.edges(data=True):
        edges_dict = {}
        edges_dict["source"] = src
        edges_dict["target"] = dst
        edges_dict["hit_count"] = 0
        edges_dict["src_function_name"] = nodes_list[tmp_idx[src]]["function_name"]
        edges_dict["src_function_source_file"] = ""
        edges_dict["dst_function_name"] = nodes_list[tmp_idx[dst]]["function_name"]
        edges_dict["dst_functoin_source_file"] = ""
        edges_list.append(edges_dict)
        edges_idx[(edges_dict["src_function_name"], edges_dict["dst_function_name"])] = idx
        idx += 1
    
    data_dict["nodes"] = nodes_list
    data_dict["edges"] = edges_list
    return [data_dict, nodes_idx, edges_idx]        


if __name__ == '__main__':
    process_cg()