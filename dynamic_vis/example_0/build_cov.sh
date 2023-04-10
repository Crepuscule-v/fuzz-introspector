if [ -d "work" ]; then
    cd work
fi

../../../build/llvm-build/bin/clang -flegacy-pass-manager -fprofile-instr-generate -fcoverage-mapping -fsanitize=fuzzer -g ../fuzzer.cpp -o fuzzer
./fuzzer -max_total_time=3
../../../build/llvm-build/bin/llvm-profdata merge -sparse default.profraw -o merged_cov.profdata
../../../build/llvm-build/bin/llvm-cov show -instr-profile=merged_cov.profdata -object=./fuzzer -line-coverage-gt=0 > fuzzer.covreport
