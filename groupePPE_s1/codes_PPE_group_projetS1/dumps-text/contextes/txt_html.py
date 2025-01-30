import os
import re

def process_files(input_dir, output_dir, keyword):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 定义 HTML 表头
    html_header = """<!DOCTYPE html>
<html>
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css\">
</head>
<body>
    <div class=\"table-container\">
      <table class=\"table is-bordered is-hoverable is-striped is-fullwidth\">
         <tr>
            <th>Contexte gauche</th>
            <th>Cible</th>
            <th>Contexte droit</th>
         </tr>\n"""

    # 定义 HTML 表尾
    html_footer = """      </table>
   </div>
</body>
</html>"""

    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename.replace('.txt', '.html'))

            with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.write(html_header)  # 写入 HTML 表头

                for line in infile:
                    line = line.strip()
                    if line:  # 跳过空行
                        # 使用正则表达式查找关键词及其前后上下文
                        match = re.search(f"(.*?){keyword}(.*)", line)
                        if match:
                            gauche = match.group(1).strip()
                            droit = match.group(2).strip()

                            # 写入格式化的 HTML 行
                            outfile.write(
                                f"              <tr>\n"
                                f"                  <td>{gauche}</td>\n"
                                f"                  <td>{keyword}</td>\n"
                                f"                  <td>{droit}</td>\n"
                                f"              </tr>\n"
                            )

                outfile.write(html_footer)  # 写入 HTML 表尾

# 使用示例
input_directory = "./contextes"  # 替换为你的输入文件夹路径
output_directory = "/home/caoyue/PPE_github/groupePPE1_2024/concordances"  # 替换为你的输出文件夹路径
keyword = "douceur"

process_files(input_directory, output_directory, keyword)

