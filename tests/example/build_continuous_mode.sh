rurROOT=$PWD
export FUZZ_INTROSPECTOR=1
# Compilation-based Static analysis
rm -r ./work ./web
mkdir work
cd work
../../../build/llvm-build/bin/clang++ -fsanitize=fuzzer -flto -g ../fuzzer.c -o fuzzer
cd ..
python3 ${ROOT}/../../src/main.py correlate --binaries_dir=./work/

# build continuous mode 
cd work
../../../build/llvm-build/bin/clang++  -fprofile-instr-generate -fcoverage-mapping -fsanitize=fuzzer -mllvm -runtime-counter-relocation ../fuzzer.c -o fuzzer
LLVM_PROFILE_FILE="fuzzer%c.profraw"  ./fuzzer