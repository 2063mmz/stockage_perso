#!/bin/bash

# 定义一个绝对路径
input="/home/caoyue/PPE_github/groupePPE1_2024/dumps-text"
output="/home/caoyue/PPE_github/groupePPE1_2024/contextes"

# 确保输出目录存在
mkdir -p "$output"

# 遍历 input_dir 目录下的所有文本文件
for file in "$input"/lang1-*.txt;
do
    # 使用 basename 提取文件名，不包括路径部分，并去掉 .txt 后缀
    filename=$(basename "$file" .txt)
    
    # 使用 grep 提取关键词 "douceur" 的上下文，并保存到对应的文件中
    grep -oiP "(\S+\s+){0,10}\bdouceur\b(\s*\S+){0,8}[\.,!?;]?" "$file" | sort | uniq > "$output/${filename}.txt"

done

