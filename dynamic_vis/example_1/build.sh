#! /bin/bash 
CLANG=../../../build/llvm-build/bin/clang++
OPT=../../../build/llvm-build/bin/opt

rm -rf ./work
mkdir work
cd work

$CLANG -S -emit-llvm ../fuzzer.cpp -o fuzzer.ll
# 导出函数调用图 CG 
$OPT -dot-callgraph -enable-new-pm=0 -disable-output fuzzer.ll
dot -Tpng fuzzer.ll.callgraph.dot -o fuzzer.ll.callgraph.png

# 导出每个函数的控制流图 CFG 
$OPT -dot-cfg -enable-new-pm=0 -disable-output fuzzer.ll

# 首先基于 fuzz-introspector 进行编译时静态分析，获取对所有函数的 func warpper 
export FUZZ_INTROSPECTOR=1
$CLANG -fsanitize=fuzzer -flto -g ../fuzzer.cpp -o fuzzer 
cd ..
# 生成 exe_to_fuzz_introspector_logs.yaml
python3 ../../src/main.py correlate --binaries_dir=./work/

# 以 continuous mode 进行 fuzz 测试
cd work
../../../build/llvm-build/bin/clang++  -fprofile-instr-generate -fcoverage-mapping -fsanitize=fuzzer -mllvm -runtime-counter-relocation ../fuzzer.cpp -o fuzzer
LLVM_PROFILE_FILE="default%c.profraw"  ./fuzzer