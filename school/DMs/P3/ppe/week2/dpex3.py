import thulac
import os
import re
import sys
from typing import List
import argparse
from tabulate import tabulate

# 初始化分词器
thu = thulac.thulac(seg_only=True)

###########################################################
# 修复后的 stdin 读取函数
###########################################################
def lire_corpus_stdin():
    # 读取所有输入行，合并为一个字符串
    all_lines = " ".join([line.strip() for line in sys.stdin])
    
    # 清理非法字符（保留法语、中文、韩文字符等）
    clair_text = re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7a3a-zA-Z'’.]", " ", all_lines)
    
    # 返回单文档列表
    return [clair_text]
###########################################################
# 中文分词函数（修复 Thulac 参数问题）
###########################################################
def seg_mots_chinois(text):
    def segment_chinese(match):
        segmented = thu.cut(match.group(), text=False)  # 返回分词列表
        return " ".join([word[0] for word in segmented])  # 拼接成分词字符串
    return re.sub(r"[\u4e00-\u9fff]+", segment_chinese, text)

###########################################################
# 其他函数保持不变（只需修复逻辑冲突）
###########################################################
def dico_occurences_mots(liste):
    corpus = (" ".join(liste)).lower()
    corpus = seg_mots_chinois(corpus)
    mots = corpus.split()
    occurences = {}
    for mot in mots:
        if not re.search(r"[a-zA-Z\u4e00-\u9fff\uac00-\ud7a3]", mot):
            continue
        occurences[mot] = occurences.get(mot, 0) + 1
    return occurences

def mots_fichier_count(mots_list, dossier):
    n_mots_list = set(m.lower() for m in mots_list)
    count_dict = {mot: 0 for mot in n_mots_list}
    for nom_f in os.listdir(dossier):
        fichiers = os.path.join(dossier, nom_f)
        with open(fichiers, 'r', encoding='utf-8', errors='ignore') as f:
            text = seg_mots_chinois(f.read()).lower()
            n_mots = set(text.split())
            for mot in n_mots_list & n_mots:
                count_dict[mot] += 1
    return count_dict

###########################################################
# 主函数（确保输入来源统一）
###########################################################
def main():
    corpus_texts = lire_corpus_stdin()
    #print("Documents lus:", corpus_texts)  # 检查读取的文档内容
    
    occurence_mots = dico_occurences_mots(corpus_texts)
    #print("Occurrences:", occurence_mots)  # 检查词频统计结果
    
    dict_mots_docs = mots_fichier_count(occurence_mots.keys(), "./Corpus")
    #print("Mots dans les documents:", dict_mots_docs)  # 检查文档计数结果
    
    # 后续代码...
    
    data = []
    for mot in sorted(occurence_mots.keys()):
        frequence = occurence_mots[mot]
        doc_compte = dict_mots_docs.get(mot, 0)
        data.append([mot, frequence, doc_compte])
    
    print(tabulate(data, headers=["Mot", "Occurence", "NB"], tablefmt="plain"))
    # 在 main() 函数中添加：
    print("数据量:", len(data))  # 如果输出为0，说明数据为空
    print("数据示例:", data[:2])  # 打印前两行数据
if __name__ == "__main__":
    main()