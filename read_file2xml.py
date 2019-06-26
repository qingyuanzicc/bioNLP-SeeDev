import os
from nltk.corpus import stopwords
import re
import numpy as np
from doc_object import *
import utils as utils


def get_type_pos(fp_type_pos):  # 这里获取 实体类型和实体位置 todo  这里获取信息 要注意 标签的单词之间有空格得情况  可以判断 t_p得长度，根据不同长度做处理
    t_p = fp_type_pos.split(' ')
    assert len(t_p) >= 3
    e_type = t_p[0]
    rests = " ".join(t_p[1:])
    # 连起来以后格式“738 756;762 782”
    pos_list = rests.split(";")
    # 若没有分号，则不分割，返回:
    # 无分号：['234 243']
    # 有分号：['234 667', '25 65']
    position = []
    for p in pos_list:
        starts, ends = p.split(" ")
        position.append((starts, ends))
    return e_type, position
    # 返回列表元组


def get_relation_and_entityid(line):
    r = line.split(' ')
    assert len(r) >= 3
    rela_type = r[0]
    entity1_type, entity1_id = r[1].split(':')
    entity2_type, entity2_id = r[2].split(':')
    return rela_type, entity1_type, entity1_id, entity2_type, entity2_id


def creat_line_obj(rootp, a1_f, doc):
    # 创建line对象和doc对象
    temp_lines = []
    lines = utils.read_file(os.path.join(rootp, a1_f))
    line_objs = list(map(lambda x: Line(x[0], doc.doc_id, x[1]), enumerate(lines)))
    doc.lines = line_objs
    doc.lines2characters()
    assert len(doc.characters) == len("\n".join(lines))
    # doc对象创建完成, 并且把line对象转化为character对象


def creat_entity_obj(rootp, a1_f, doc):
    with open(os.path.join(rootp, a1_f), encoding='utf-8') as f2:
        entity_line = f2.read().splitlines()  # 读取entities
    entities_line = list(filter(lambda x: x.strip() != "", entity_line))  # 去掉空行
    if len(entities_line) > 0:
        all_characters = doc.characters  # 获取原文
        for e in entities_line:
            t_id, type_pos, text = e.split('\t')
            entity_type, pos = get_type_pos(type_pos)  # 获取信息
            temp_text_list = []

            entity_object = Entity(t_id, text, pos, entity_type, doc.doc_id)
            for en in entity_object.pos:
                start = int(en[0])
                end = int(en[1])
                temp_text_list.append("".join(map(lambda x: x.text, d.characters[start:end])).strip())
            assert entity_object.text == " ".join(temp_text_list).replace("\n", " ").strip()
            temp_text_list.clear()

            # pos的格式：[('4780', '4800')]
            doc.entities.append(entity_object)  # 保存到当前doc对象得entities中


def creat_relation_obj(rootp, a2_f, doc):
    with open(os.path.join(rootp, a2_f), encoding="utf-8") as f3:  # 读取实体标注文件
        relation_line = f3.read().splitlines()  # relation
    relation_line = list(filter(lambda x: x.strip() != '', relation_line))
    if len(relation_line) > 0:
        temp = []
        rid2eid = {}
        for rest in relation_line:
            r_id, type_pos = rest.split('\t')
            r_type, e1_type, e1_id, e2_type, e2_id = get_relation_and_entityid(type_pos)
            e1 = list(filter(lambda x: x.id == e1_id, doc.entities))[0]
            e2 = list(filter(lambda x: x.id == e2_id, doc.entities))[0]
            rid2eid[r_id] = e1.id + ' ' + e2.id
            temp.append([e1.id, e2.id])
            relation_object = Relation(r_id, r_type, e1, e2, e1_type, e2_type)
            doc.relations.append(relation_object)
        assert len(temp) == len(relation_line)
        doc.multi_relation = utils.two_e_have_multi_r(temp, rid2eid, doc.relations)


def creat_sentence_obj(doc):
    # 接下来创建句子对象，调用utils里面的方法：
    sents = utils.split2sentence(doc)
    # 切分完句子以后，验证根据坐标找到的单词和原单词是否一致
    for entity in doc.entities:
        if len(entity.pos) == 1:
            assert isinstance(entity.text, str)
            assert isinstance(entity.pos, list)

    # 验证完以后，获取每个句子ID、有哪些实体、有哪些关系等等
    # 首先计算每个句子长度
    sent_len_list = [len(sents[i]) for i in range(len(sents))]
    i = 0
    for s_id, sent in enumerate(sents):
        sent_id = s_id
        sent_len = sent_len_list[s_id]
        start = i
        end = i + sent_len
        i = i + sent_len
        sent_start2end_index = (start, end)
        # _, sent_words_num = utils.count_words_in_each_sentence(sent)
        sent_text = sents[s_id]
        sentence_object = Sentence(sent_id, sent_len, sent_start2end_index,
                                   0, sent_text)
        doc.sentences.append(sentence_object)
    # 调用方法:查找每句话中的实体
    utils.retrieve_entities(doc)
    # 调用方法:查找每句话中的关系
    utils.retrieve_relations(doc)
    for s in doc.sentences:
        s.init()


def creat_word_obj(doc):
    for sent_obj in doc.sentences:
        words_list, words_num = utils.count_words_in_each_sentence(sent_obj.text)
        for word in words_list:
            word_id = 0
            word_text = word
            # word_freq =
            # word_in_which_sent =
            # is_entit =
            # belong2which_t_id =
            # is_related_to_another_entity =
            # ridtid =
            # word_object = Word(word_id, word_text, word_freq, word_in_which_sent, is_entit, belong2which_t_id, is_related_to_another_entity, ridtid)
            # d.words.append(word_object)


if __name__ == '__main__':
    # file_root_path = '../bioNLP-SeeDev/BioNLP-ST-2016_SeeDev-binary_train/'
    file_root_path = 'E:/bioNLP-SeeDev/BioNLP-ST-2016_SeeDev-binary_train'
    result = []
    for rt, dirs, files in os.walk(file_root_path):
        if len(files) > 0:
            for f in files:
                if not f.endswith('txt'):
                    continue
                a1_file = os.path.splitext(f)[0] + '.a1'
                a2_file = os.path.splitext(f)[0] + '.a2'
                d = Doc()
                d.doc_id = os.path.splitext(f)[0]

                creat_line_obj(rt, f, d)
                creat_entity_obj(rt, a1_file, d)
                creat_relation_obj(rt, a2_file, d)
                creat_sentence_obj(d)
                creat_word_obj(d)
                result.append(d)
    # sum(list(map(lambda x: len(x), list(map(lambda x: x.skip_sentence_relation, result)))
    if not os.path.exists('./saved_data'):  # 52 个跨句关系 总共1628个关系 630句话
        os.makedirs('./saved_data')
    utils.dumpData4Gb(result, r'./saved_data/train.bin')
