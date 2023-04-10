import sys
sys.path.append("../../src/")

from fuzz_introspector import constants, analysis, cfg_load
from fuzz_introspector.datatypes import fuzzer_profile
from process_cg import process_cg
import logging, os, shlex
import time, subprocess
logger = logging.getLogger(name=__name__)

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
    data_dict = 
    for profile in introspector_target.profiles:
        for node in cfg_load.extrace_all_callsite(profile.fuzzer_callsite_calltree):
            print("-------------")
            print(node.dst_function_name)
            print(node.src_function_name)
            print("-------------")
        # cfg_load.print_ctcs_tree(profile.fuzzer_callsite_calltree)
        
    exit(0)
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


def run():
    introspection_target = build_introspection_proj()
    while True:
        # 没更新一次所需要的时间大概为 0.01s 
        update_coverage_info()  # 从 profraw 中读取覆盖信息，并进行相关处理
        
        # 根据 profdata 为该对象写入覆盖信息
        for profile in introspection_target.profiles:
            profile.accummulate_profile( introspection_target.base_folder)
            analysis.overlay_calltree_with_coverage(profile, introspection_target.proj_profile, introspection_target.coverage_url, introspection_target.base_folder)
            cp = profile.coverage
            # print(cp.covmap)
            # print(cp.coverage_files)
            # print(cp.branch_cov_map)
        with open("result.json", "a") as file:
            file.write(str(cp.covmap))


if __name__ == "__main__":
    set_logging_level()
    run()


