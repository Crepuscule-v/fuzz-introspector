#！/bin/bash
COVREOPRT_PATH=/home/fuzz/Desktop/fuzz-introspector/tests/example
EXECUTE_COMMAND() {
    ../../build/llvm-build/bin/llvm-profdata merge -sparse ./work/fuzzer.profraw -o ./work/merged_cov.profdata
    ../../build/llvm-build/bin/llvm-cov show -instr-profile=./work/merged_cov.profdata -object=./work/fuzzer -line-coverage-gt=0 > ./work/fuzzer.covreport
    ../../build/llvm-build/bin/llvm-cov show --format=html -instr-profile=./work/merged_cov.profdata -object=./work/fuzzer > $COVREOPRT_PATH/fuzzer.c.html
    # cat fuzzer.covreport
    cd web/
    python3 ../../../src/main.py report --correlation_file=../exe_to_fuzz_introspector_logs.yaml --target_dir=../ --coverage_url=""
    cd ..
}

mkdir ./web

while true; do
    EXECUTE_COMMAND
    sleep 1
done
