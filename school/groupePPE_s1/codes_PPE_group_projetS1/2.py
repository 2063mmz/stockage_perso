import csv

# 定义输入和输出文件名
input_file = '3.tsv'
output_file = '1.html'

# 读取TSV文件并生成HTML表格内容
with open(input_file, newline='', encoding='utf-8') as tsvfile:
    reader = csv.reader(tsvfile, delimiter='\t')
    headers = next(reader)  # 跳过表头行

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Tableau de résultats</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
    <style>
        table {{
            table-layout: auto; 
            width: 100%; 
        }}
        th, td {{
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <table class="table is-bordered">
        <caption class="has-text-info">Les résultats des URLs qui contiennent le mot : bien</caption>
        <thead>
            <tr>
                <th class="is-link">num</th>
                <th class="is-primary">URLs</th>
                <th class="is-warning">Statut HTTP</th>
                <th class="is-success">Nb de mots</th>
                <th class="is-danger">L'encodage</th>      
            </tr>
        </thead>
        <tbody>
"""

    row_number = 1
    for row in reader:
        num, url, Encoding, Status, nb_mot_total, nb_mot_cle = row
        html_content += f"""
            <tr>
                <td>{num}</td>
                <td><a href="{url}" target="_blank">{url}</a></td>
                <td>{Encoding}</td>
                <td>{Status}</td>
                <td>{nb_mot_total}</td>
                <td>{nb_mot_cle}</td>
            </tr>
"""
        row_number += 1

    html_content += """
        </tbody>
    </table>
    <body>
        <a href="../index.html" class="button">Retour à l'accueil</a>
    </body>
</body>
</html>
"""

# 写入HTML文件
with open(output_file, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"HTML file created: {output_file}")
