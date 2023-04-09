; ModuleID = 'fuzzer.cpp'
source_filename = "fuzzer.cpp"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

; Function Attrs: mustprogress noinline nounwind optnone uwtable
define dso_local noundef i64 @_Z23count_uppercase_lettersPKhm(i8* noundef %data, i64 noundef %size) #0 {
entry:
  %data.addr = alloca i8*, align 8
  %size.addr = alloca i64, align 8
  %count = alloca i64, align 8
  %i = alloca i64, align 8
  store i8* %data, i8** %data.addr, align 8
  store i64 %size, i64* %size.addr, align 8
  store i64 0, i64* %count, align 8
  store i64 0, i64* %i, align 8
  br label %for.cond

for.cond:                                         ; preds = %for.inc, %entry
  %0 = load i64, i64* %i, align 8
  %1 = load i64, i64* %size.addr, align 8
  %cmp = icmp ult i64 %0, %1
  br i1 %cmp, label %for.body, label %for.end

for.body:                                         ; preds = %for.cond
  %2 = load i8*, i8** %data.addr, align 8
  %3 = load i64, i64* %i, align 8
  %arrayidx = getelementptr inbounds i8, i8* %2, i64 %3
  %4 = load i8, i8* %arrayidx, align 1
  %conv = zext i8 %4 to i32
  %cmp1 = icmp sge i32 %conv, 65
  br i1 %cmp1, label %land.lhs.true, label %if.end

land.lhs.true:                                    ; preds = %for.body
  %5 = load i8*, i8** %data.addr, align 8
  %6 = load i64, i64* %i, align 8
  %arrayidx2 = getelementptr inbounds i8, i8* %5, i64 %6
  %7 = load i8, i8* %arrayidx2, align 1
  %conv3 = zext i8 %7 to i32
  %cmp4 = icmp sle i32 %conv3, 90
  br i1 %cmp4, label %if.then, label %if.end

if.then:                                          ; preds = %land.lhs.true
  %8 = load i64, i64* %count, align 8
  %inc = add i64 %8, 1
  store i64 %inc, i64* %count, align 8
  br label %if.end

if.end:                                           ; preds = %if.then, %land.lhs.true, %for.body
  br label %for.inc

for.inc:                                          ; preds = %if.end
  %9 = load i64, i64* %i, align 8
  %inc5 = add i64 %9, 1
  store i64 %inc5, i64* %i, align 8
  br label %for.cond, !llvm.loop !4

for.end:                                          ; preds = %for.cond
  %10 = load i64, i64* %count, align 8
  ret i64 %10
}

; Function Attrs: mustprogress noinline nounwind optnone uwtable
define dso_local i32 @LLVMFuzzerTestOneInput(i8* noundef %data, i64 noundef %size) #0 {
entry:
  %data.addr = alloca i8*, align 8
  %size.addr = alloca i64, align 8
  store i8* %data, i8** %data.addr, align 8
  store i64 %size, i64* %size.addr, align 8
  %0 = load i8*, i8** %data.addr, align 8
  %1 = load i64, i64* %size.addr, align 8
  %call = call noundef i64 @_Z23count_uppercase_lettersPKhm(i8* noundef %0, i64 noundef %1)
  ret i32 0
}

attributes #0 = { mustprogress noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.module.flags = !{!0, !1, !2}
!llvm.ident = !{!3}

!0 = !{i32 1, !"wchar_size", i32 4}
!1 = !{i32 7, !"uwtable", i32 1}
!2 = !{i32 7, !"frame-pointer", i32 2}
!3 = !{!"clang version 14.0.6 (https://github.com/llvm/llvm-project/ f28c006a5895fc0e329fe15fead81e37457cb1d1)"}
!4 = distinct !{!4, !5}
!5 = !{!"llvm.loop.mustprogress"}
