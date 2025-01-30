import os
import string

# 输入输出目录
input_dir = '/home/caoyue/PPE_github/git-along/save_some_code/code_PPE/essais/dumps-text'  # 输入文件夹，包含所有txt文件
output_dir = '/home/caoyue/PPE_github/git-along/save_some_code/code_PPE/essais/dumps-text/contextes/pal/dumps_pals'  # 输出文件夹，保存处理后的文件

# 检查输出文件夹是否存在，不存在则创建
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 定义需要去除的特殊标点符号
punctuation_to_remove = ".,!?()[]{}<>:;\""

# 遍历输入目录中的所有txt文件
for input_filename in os.listdir(input_dir):
    if input_filename.endswith('*.txt'):
        input_filepath = os.path.join(input_dir, input_filename)
        output_filepath = os.path.join(output_dir, f'{os.path.splitext(input_filename)[0]}.txt')
        
        with open(input_filepath, 'r', encoding='utf-8') as infile, open(output_filepath, 'w', encoding='utf-8') as outfile:
            # 逐行读取输入文件
            for line in infile:
                # 按空格拆分句子为单词
                words = line.split()
                
                # 处理每个单词，去除特殊标点符号
                processed_words = []
                for word in words:
                    # 去除特殊标点符号（保留词中的撇号，如 d'une）
                    processed_word = word.translate(str.maketrans('', '', punctuation_to_remove))
                    if processed_word:  # 只输出非空的单词
                        processed_words.append(processed_word)
                
                # 将处理后的单词写入输出文件，每个单词单独一行
                for word in processed_words:
                    outfile.write(word + '\n')
                
                # 在每句结束后加一个空行（分隔句子）
                outfile.write('\n')
        
        print(f'处理完毕: {input_filepath} -> {output_filepath}')

