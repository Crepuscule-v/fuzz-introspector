import sys, constant_val
sys.path.append(constant_val.FUZZ_INTROSPECTOR_SRC_DIR)
from fuzz_introspector import constants, analysis, cfg_load
from fuzz_introspector.datatypes import fuzzer_profile
from fuzz_introspector.code_coverage import CoverageProfile
from process_cg import process_cg, demangle_cpp_func
import logging, os, shlex
import time, subprocess, json
logger = logging.getLogger(name=__name__)

data_dict = {}
nodes_idx = {}
edges_dict= {}

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

def build_introspection_proj() -> analysis.IntrospectionProject :
    language = "c-cpp"
    target_dir = "./work/"
    coverage_url = ""
    correlation_file = "./exe_to_fuzz_introspector_logs.yaml"
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
        # cfg_load.print_ctcs_tree(profile.fuzzer_callsite_calltree)
    
    data_dict = {
        "nodes" : nodes_dict,
        "edges" : edges_dict
    }
    # with open("./work/datadict.json", "w") as file:
    #     json.dump(data_dict, file)
    
    return introspector_target

def parse_command(command_str) -> list:
    return shlex.split(command_str)

def update_coverage_info():
    BASH_COMMAND_LIST = ["../../build/llvm-build/bin/llvm-profdata merge -sparse ./work/default.profraw -o ./work/merged_cov.profdata",
                         "../../build/llvm-build/bin/llvm-cov show -instr-profile=./work/merged_cov.profdata -object=./work/fuzzer -line-coverage-gt=0",
                         "../../build/llvm-build/bin/llvm-cov show --format=html -instr-profile=./work/merged_cov.profdata -object=./work/fuzzer"
    ]

    cmd0 = parse_command(BASH_COMMAND_LIST[0])
    cmd1 = parse_command(BASH_COMMAND_LIST[1])
    cmd2 = parse_command(BASH_COMMAND_LIST[2])
    
    subprocess.run(cmd0, check=True)
    with open("./work/fuzzer.covreport", "w") as outfile:
        subprocess.run(cmd1, check=True, stdout=outfile)
    with open("./fuzzer.c.html", "w") as outfile:
        subprocess.run(cmd2, check=True, stdout=outfile)

def update_data_dict(cp : CoverageProfile):
    pass


def run():
    introspection_target = build_introspection_proj()
    while True:
        # 每更新一次所需要的时间大概为 0.01s 
        update_coverage_info()  # 从 profraw 中读取覆盖信息，并进行相关处理
        
        # 根据 profdata 更新该对象的覆盖信息, 并更新 data_dict
        for profile in introspection_target.profiles:
            profile.accummulate_profile( introspection_target.base_folder)
            analysis.overlay_calltree_with_coverage(profile, introspection_target.proj_profile, introspection_target.coverage_url, introspection_target.base_folder)
            cp = profile.coverage
            update_data_dict(cp)
            # print(cp.covmap)
            # print(cp.coverage_files)
            # print(cp.branch_cov_map)
        with open("result.json", "a") as file:
            json.dump(cp.covmap, file)
        exit(0)

if __name__ == "__main__":
    set_logging_level()
    run()