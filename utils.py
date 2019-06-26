import json
import pickle
import re
from collections import Counter
import numpy as np
import jieba
import os
import shutil
import torch
from nltk.corpus import stopwords
from stanfordcorenlp import StanfordCoreNLP


def read_file(path):
    with open(path, "r", encoding='utf-8') as f1:
        data = f1.read().splitlines()
    return data
    # 返回一个list, 每个元素是一行字符


def dumpData4Gb(data, openPath):
    with open(openPath, "wb") as file:
        pickle.dump(data, file, protocol=4)


def split2sentence(d):
    s = "".join(list(map(lambda x: x.text, d.characters)))
    s = s.replace('\n', ' ')
    first_word = re.findall(r"[\.\?\!]\s?[A-Z]+\w+", s)
    sent = re.split(r'[\.\?\!]\s?[A-Z]+\w+', s)
    new_sents = [w + z for w, z in zip(first_word, sent[1:])]
    new_sents.insert(0, sent[0])

    sent_identifiers = ['.', '?', '!']
    for char in sent_identifiers:
        for i, pre_sent in enumerate(new_sents):
            if pre_sent.startswith(char):
                pre_sent = pre_sent.replace(char, '', 1)
                new_sents[i - 1] = new_sents[i - 1] + char
                for chara in pre_sent:
                    if chara.find(' ') == 0 and chara == ' ':
                        pre_sent = pre_sent.replace(' ', '', 1)
                        new_sents[i - 1] = new_sents[i - 1] + ' '
                        break
                    break
                new_sents[i] = pre_sent
    return new_sents


def count_words_in_each_sentence(sentence):
    nlp = StanfordCoreNLP('E:\TOOLS\stanford-corenlp-full-2018-10-05', lang='en')
    return nlp.word_tokenize(sentence), len(nlp.word_tokenize(sentence))


def retrieve_entities(d):
    for each_t in d.entities:
        start = int(each_t.pos[0][0])
        end = int(each_t.pos[-1][-1])
        entity_in_sentence = list(filter(lambda x: x.s_start2end_index[0] <= start
                                                   and x.s_start2end_index[-1] >= end, d.sentences))
        assert len(entity_in_sentence) != 0
        entity_in_sentence[0].entitys.append(each_t)


def retrieve_relations(d):
    for relation in d.relations:
        e1 = relation.entity1
        e2 = relation.entity2
        realtion_in_sentence = list(filter(lambda x: e1 in x.entitys and e2 in x.entitys, d.sentences))
        if len(realtion_in_sentence) == 0:
            relation.skip_sentence = 1
            d.skip_sentence_relation.append(relation)
        else:
            realtion_in_sentence[0].relations.append(relation)


def two_e_have_multi_r(ls, r2e_dict, doc_r_obj):
    new = []
    for i in ls:
        new.append(' '.join(sorted(i)))
    count = Counter(new)
    multi_r_list = []
    for ele, num in count.items():
        assert num <= 2
        if num == 2:
            multi_r_list.append((list(filter(lambda x: r2e_dict[x.id] == ele, doc_r_obj)), num))
    return multi_r_list
