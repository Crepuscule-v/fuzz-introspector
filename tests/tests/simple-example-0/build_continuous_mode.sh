../../build/llvm-build/bin/clang++ -flegacy-pass-manager -fprofile-instr-generate -fcoverage-mapping -fsanitize=fuzzer  ../fuzzer.c -o fuzzer
echo "grabege" > fuzzer.profraw
LLVM_PROFILE_FILE="%cfuzzer.profraw"  ./fuzzer
