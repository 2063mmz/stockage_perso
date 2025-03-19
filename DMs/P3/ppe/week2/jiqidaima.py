import thulac
import os
import re
import sys
from typing import List

###########################################################
# script r1
###########################################################

dossier = "./Corpus"  # 确保目录正确
thu = thulac.thulac(seg_only=True)  # 初始化分词器

def seg_mots_chinois(text):
    """只对文本中的中文部分进行分词，其他语言保持不变"""
    def segment_chinese(match):
        return thu.cut(match.group(), text=True)  # 返回用空格分隔的中文分词结果

    # 仅处理中文字符块
    return re.sub(r"[\u4e00-\u9fff]+", segment_chinese, text)

def lire_corpus(dossier):
    """读取语料库并清理文本"""
    if not os.path.isdir(dossier):
        print(f"目录 '{dossier}' 不存在")
        return []

    contenus = []
    for fichier in os.listdir(dossier):
        chemin = os.path.join(dossier, fichier)
        if os.path.isfile(chemin):
            try:
                with open(chemin, "r", encoding="utf-8") as f:
                    text = f.read()
                    # 保留字母、汉字、韩文、法文字符及常用标点
                    cleaned = re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7afa-zA-Z'’.]", " ", text)
                    contenus.append(cleaned)
            except Exception as e:
                print(f"读取文件 {fichier} 失败: {e}")
    return contenus

###########################################################
# script r2
###########################################################

def dico_occurences_mots(liste):
    """统计总词频（统一小写处理）"""
    corpus = seg_mots_chinois(" ".join(liste)).lower()
    mots = corpus.split()
    
    occurences = {}
    for mot in mots:
        # 过滤无效词（需包含至少一个字母或汉字）
        if not re.search(r"[a-zA-Z\u4e00-\u9fff]", mot):
            continue
        occurences[mot] = occurences.get(mot, 0) + 1
    return occurences

def mots_fichier_count(mots_list, dossier):
    """统计文档频率（优化性能版）"""
    # 预处理：去重并统一小写
    mots_set = set(m.lower() for m in mots_list)
    count_dict = {mot:0 for mot in mots_set}

    for filename in os.listdir(dossier):
        path = os.path.join(dossier, filename)
        if not os.path.isfile(path):
            continue
        
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                # 处理文本并分词
                text = seg_mots_chinois(f.read()).lower()
                doc_words = set(text.split())
                
                # 更新文档计数
                for word in doc_words & mots_set:
                    count_dict[word] += 1
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
    
    return count_dict

###########################################################
# MAIN
###########################################################

def main():
    # 1. 读取语料
    corpus = lire_corpus(dossier)
    print(f"成功读取 {len(corpus)} 个文档")

    # 2. 统计词频
    freq_dict = dico_occurences_mots(corpus)
    print(f"共发现 {len(freq_dict)} 个唯一词语")

    # 3. 统计文档频率
    doc_freq = mots_fichier_count(freq_dict.keys(), dossier)

    # 4. 写入结果
    with open("resultats.tsv", "w", encoding="utf-8") as f:
        f.write("单词\t总出现次数\t出现文档数\n")
        for mot in sorted(freq_dict):
            f.write(f"{mot}\t{freq_dict[mot]}\t{doc_freq.get(mot, 0)}\n")
    
    print("结果已保存至 resultats.tsv")

if __name__ == "__main__":
    main()