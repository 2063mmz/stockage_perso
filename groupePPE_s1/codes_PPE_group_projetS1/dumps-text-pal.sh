#!/bin/bash

# 输入和输出目录
input_dir="/home/caoyue/PPE_github/git-along/save_some_code/code_PPE/essais/dumps-text/contextes"       # 输入目录，包含所有的 .txt 文件
output="/home/caoyue/PPE_github/git-along/save_some_code/code_PPE/essais/dumps-text/contextes/pal/contextes_pals/contextes-lang1.txt"  # 输出目录，保存处理后的文件

# 检查输入目录是否存在
if [ ! -d "$input_dir" ]; then
    echo "Input directory '$input_dir' does not exist."
    exit 1
fi

# 清空输出文件（如果已存在）
> "$output"

# 遍历输入目录中的所有 .txt 文件
for file in "$input_dir"/lang1-*.txt; do
    
    # 处理文件内容并追加到输出文件
    sed "s/[,.!?()]//g; s/  */ /g" "$file" |tr ' ' '\n' >> "$output"
done
sed '/^$/d' "$output" > temp && mv temp "$output"
echo "All files have been processed. Combined output is in '$output'."

