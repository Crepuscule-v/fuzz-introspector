import sys, constant_val
sys.path.append(constant_val.FUZZ_INTROSPECTOR_SRC_DIR)

from fuzz_introspector import constants, analysis, cfg_load
from fuzz_introspector.datatypes import fuzzer_profile
from fuzz_introspector.code_coverage import CoverageProfile
from process_cg import process_cg, demangle_cpp_func
import logging, os, shlex
import subprocess, json
import random
from typing import Dict, List 
logger = logging.getLogger(name=__name__)

def random_color():
    color = '#{:02X}{:02X}{:02X}'.format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # print(color)
    return color

def set_logging_level() -> None:
    if os.environ.get("FUZZ_LOGLEVEL"):
        level = os.environ.get("FUZZ_LOGLEVEL")
        if level == "debug":
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)
    logger.debug("Logging level set")

def build_introspection_proj() -> List:
    '''
    静态初始化
    '''
    language = "c-cpp"
    target_dir = "./example_1/work/"
    coverage_url = ""
    correlation_file = "./example_1/exe_to_fuzz_introspector_logs.yaml"

    # 构建一个 introspection 对象
    introspector_target = analysis.IntrospectionProject(language, target_dir, coverage_url)
    introspector_target.load_data_files(True, correlation_file)
    data_dict, nodes_idx, edges_idx = process_cg()
    nodes_dict = data_dict["nodes"]
    edges_dict = data_dict["edges"]

    # 完善 data_dict 中 nodes 和 edges 对应的内容
    # nodes
    for profile in introspector_target.profiles:
        for func_name in profile.all_class_functions:
            idx = nodes_idx[func_name][0]
            nodes_dict[idx]["function_source_file"] = profile.all_class_functions[func_name].function_source_file
            nodes_dict[idx]["arg_count"] = profile.all_class_functions[func_name].arg_count
            nodes_dict[idx]["bb_count"] = profile.all_class_functions[func_name].bb_count
            nodes_dict[idx]["i_count"] = profile.all_class_functions[func_name].i_count
            nodes_dict[idx]["edge_count"] = profile.all_class_functions[func_name].edge_count
            nodes_dict[idx]["function_linenumber"] = profile.all_class_functions[func_name].function_linenumber            
    
    # edges
    for profile in introspector_target.profiles:
        for node in cfg_load.extract_all_callsites(profile.fuzzer_callsite_calltree):
            if node.src_function_name != None:
                idx = edges_idx[(demangle_cpp_func(node.src_function_name), demangle_cpp_func(node.dst_function_name))]
                edges_dict[idx]["src_function_source_file"] = node.src_function_source_file
                edges_dict[idx]["dst_function_source_file"] = node.dst_function_source_file
            # 特别标记函数入口点 LLVMFuzzerTestOneInput
            else:
                entry_func_dict = {
                    "source"  : "-1",
                    "target"  : nodes_idx[node.dst_function_name][1],
                    "hit_count" : 0,
                    "src_function_name" : "-1",
                    "src_function_source_file"  : "-1",
                    "dst_function_name" : node.dst_function_name,
			        "dst_functoin_source_file" : node.dst_function_source_file
                }
                edges_dict.append(entry_func_dict)
                edges_idx[("-1", node.dst_function_name)] = len(edges_dict) - 1

        # cfg_load.print_ctcs_tree(profile.fuzzer_callsite_calltree)
    
    data_dict = {
        "nodes" : nodes_dict,
        "edges" : edges_dict
    }
    
    return introspector_target, data_dict, nodes_idx, edges_idx

def parse_command(command_str) -> list:
    return shlex.split(command_str)

def update_coverage_info():
    BASH_COMMAND_LIST = ["../build/llvm-build/bin/llvm-profdata merge -sparse ./example_1/work/default.profraw -o ./example_1/work/merged_cov.profdata",
                         "../build/llvm-build/bin/llvm-cov show -instr-profile=./example_1/work/merged_cov.profdata -object=./example_1/work/fuzzer -line-coverage-gt=0",
                         "../build/llvm-build/bin/llvm-cov show --format=html -instr-profile=./example_1/work/merged_cov.profdata -object=./example_1/work/fuzzer"
    ]

    cmd0 = parse_command(BASH_COMMAND_LIST[0])
    cmd1 = parse_command(BASH_COMMAND_LIST[1])
    cmd2 = parse_command(BASH_COMMAND_LIST[2])
    
    subprocess.run(cmd0, check=True)
    with open("./example_1/work/fuzzer.covreport", "w") as outfile:
        subprocess.run(cmd1, check=True, stdout=outfile)
    with open("./example_1/fuzzer.c.html", "w") as outfile:
        subprocess.run(cmd2, check=True, stdout=outfile)

def update_nodes_dict(nodes_cp : CoverageProfile, data_dict, nodes_idx, edges_idx) -> Dict:
    '''
    分别更新 nodes 和 edges 对应的 hit_count
    '''
    for func_name in nodes_cp.covmap:
        cov_info = nodes_cp.covmap[func_name]
        if func_name in nodes_idx:
            idx = nodes_idx[func_name][0]
            data_dict["nodes"][idx]["hit_count"] = cov_info[0][1]
            data_dict["nodes"][idx]["color"] = random_color()               # 暂时先随机一个颜色来代替
            logger.info("update color")
        else:
            logger.error(f"Mismatched function name: {func_name}")
    return data_dict

def update_edges_dict(edges_cp, data_dict, nodes_idx, edges_idx) -> Dict:
    for node in edges_cp:
        if node.src_function_name != None:
            src_func_name = demangle_cpp_func(node.src_function_name)
            dst_func_name = demangle_cpp_func(node.dst_function_name) 
            idx = edges_idx[(src_func_name, dst_func_name)]
            data_dict["edges"][idx]["hit_count"] = node.cov_hitcount
        else:
            idx = len(data_dict["edges"]) - 1
            data_dict["edges"][idx]["hit_count"] = node.cov_hitcount
    return data_dict
    

# TODO : 需要添加更新颜色的部分
def update(introspector_target : analysis.IntrospectionProject, data_dict, nodes_idx, edges_idx) -> Dict:
    # 每更新一次所需要的时间大概为 0.01s 
    # 从 profraw 中读取覆盖信息，并进行相关处理
    update_coverage_info()  
    
    # 根据 profdata 更新该对象的覆盖信息, 并更新 data_dict
    for profile in introspector_target.profiles:
        profile.accummulate_profile(introspector_target.base_folder)
        analysis.overlay_calltree_with_coverage(profile, introspector_target.proj_profile, introspector_target.coverage_url, introspector_target.base_folder)
        nodes_cp = profile.coverage
        edges_cp = cfg_load.extract_all_callsites(profile.fuzzer_callsite_calltree)
        data_dict = update_nodes_dict(nodes_cp, data_dict, nodes_idx, edges_idx)
        data_dict = update_edges_dict(edges_cp, data_dict, nodes_idx, edges_idx)
    
    return data_dict
        # with open("./example_1/work/datadict.json", "w") as file:
        #         json.dump(data_dict, file)

def run():
    """
    用于本地测试
    """
    introspector_target, data_dict, nodes_idx, edges_idx = build_introspection_proj()
    while True:
        update(introspector_target, data_dict, nodes_idx, edges_idx)

if __name__ == "__main__":
    set_logging_level()
    run()