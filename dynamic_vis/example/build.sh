#! /bin/bash 
CLANG=../../build/llvm-build/bin/clang++
OPT=../../build/llvm-build/bin/opt

$CLANG -S -emit-llvm fuzzer.cpp -o fuzzer.ll

# 导出函数调用图 CG 
$OPT -dot-callgraph -enable-new-pm=0 -disable-output fuzzer.ll

# 导出每个函数的控制流图 CFG 
$OPT -dot-cfg -enable-new-pm=0 -disable-output fuzzer.ll

