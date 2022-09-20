# imit
提供交互或命令行的形式规范地提交git commit

## Usage:
    imit.py config
    imit.py [-m|-b|-f|-R|-r] [-1|-2|-3|-4] [-M <msg>|<msg>] [-h|--help] [--log_level=<log_level>]

## Options:
    -h,--help                   show usage
    -m                          set commit type: modify
    -b                          set commit type: bugfix
    -f                          set commit type: feature
    -R                          set commit type: refactor
    -r                          set commit type: revert
    -1                          1st version number +1
    -2                          2nd version number +1
    -3                          3rd version number +1
    -4                          4th version number +1
    -M <msg>                    set commit message
    <msg>                       set commit message easily
    --log_level=<log_level>     set log level: notset,debug,info,warn,error,fatal,critical

## 自动选择默认信息的策略
- commit_msg 中如果含有['修复','bug'], 则设置默认commit_type为bugfix
- commit_type为feature或者refactor时，设置默认version_index为-2
