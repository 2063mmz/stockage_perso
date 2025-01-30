#!/bin/bash

URLs="urls.txt"
output_file="URLs.tsv"

if [ ! -f "$URLs" ]; then
    echo "Le fichier $URLs doit contenir des URLs."
    exit 1
fi

# 清空或创建输出文件，并写入表头
echo -e "Numero\tURL\tCode HTTP\tEncodage\tCompte\tOccurrence" > "$output_file"

num=1

# 从 urls.txt 文件中读取每个 URL
while IFS= read -r line;
do
    if [[ $line =~ ^http[s]?:// ]]; then
        url="$line"
        # Suivre les redirections avec curl et obtenir le dernier URL
        info_head=$(curl -s -w "\n%{http_code}\n%{content_type}\n" -o /dev/null -L "$url")

        # 提取状态码和内容类型
        Status=$(echo "$info_head" | tail -n2 | head -n1)

        if [ "$Status" -eq 200 ]; then
            Encoding=$(echo "$info_head" | tail -n1 | sed 's/.*=//' )

            text=$(curl -s -L "$url")
            nb_mot_total=$(echo "$text" | wc -w)
            nb_mot_cle=""
            mot_cle="douceur"
            nb_mot_cle=$(echo "$text" | grep -o -i "$mot_cle" | wc -l)

            echo -e "$num\t$url\t$Status\t$Encoding\t${nb_mot_cle}" >> "$output_file"
            ((num++))
        else
            echo "Skipping $url due to non-200 status code: $Status"
        fi
    fi
done < "$URLs"

