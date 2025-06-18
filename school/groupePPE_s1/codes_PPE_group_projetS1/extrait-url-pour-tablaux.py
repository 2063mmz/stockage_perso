import csv

# 读取TSV文件的函数
def read_tsv(file_path):
    url_data = {}
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')

        for row in reader:
            print(f"Row: {row}")  # 用于调试，检查每一行数据
            url = row['URL']
            url_data[url] = {
                'Encoding': row.get('Encodage', 'N/A'),  # 使用 row.get() 获取字段
                'Status': row.get('Code HTTP', 'N/A'),   # 同样使用 row.get()
                'nb_mot_cle': row.get('Occurrence', 'N/A')  # 如果没有此字段则返回 'N/A'
            }
    return url_data

# 生成HTML表格的函数
def generate_html_table(urls, url_data):
    html_content = """
    <!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css">
</head>
<body>
    <div class="table-container">
        <h1 class="title has-text-centered">Tableau Français</h1>
        <table class="table is-bordered is-hoverable is-striped is-fullwidth">
            <thead>
                <tr>
                    <th>Numero</th>
                    <th>URL</th>
                    <th>Code HTTP</th>
                    <th>Encodage</th>
                    <th>Aspiration</th>
                    <th>Dump</th>
                    <th>Occurrence</th>
                    <th>Contexte</th>
                    <th>Concordance</th>
                </tr>
            </thead>
            <tbody>
    """

    for index, url in enumerate(urls, start=1):
        # 获取对应的 url 数据
        data = url_data.get(url, {})
        encoding = data.get('Encoding', 'N/A')
        status = data.get('Status', 'N/A')
        nb_mot_cle = data.get('nb_mot_cle', 'N/A')

        html_content += f"""
            <tr>
                <td>{index}</td>
                <td><a href="{url}" target="_blank">{url}</a></td>
                <td>{status}</td>
                <td>{encoding}</td>
                <td><a href="../aspirations/lang1-{index}.html">html</a></td>
                <td><a href="../dumps-text/lang1-{index}.txt">dump-text</a></td>
                <td>{nb_mot_cle}</td>
                <td><a href="../contextes/lang1-{index}.txt">contexte</a></td>
                <td><a href="../concordances/lang1-{index}.html">concordance</a></td>
            </tr>
        """

    html_content += """
         </tbody>
        </table>
    </div>
</body>
</html>
"""
    return html_content

# 主函数
def main():
    # 读取 TSV 文件
    url_data = read_tsv('URLs.tsv')

    # 提取 URL 列表
    urls = list(url_data.keys())

    # 生成 HTML 表格
    html_content = generate_html_table(urls, url_data)

    # 输出 HTML 内容到文件
    with open('/home/caoyue/PPE_github/groupePPE1_2024/tableaux/lang1.html', 'w') as output_file:
        output_file.write(html_content)
    print("HTML table has been generated successfully.")

# 执行主函数
if __name__ == "__main__":
    main()

