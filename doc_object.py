import numpy
import re
import os
import collections


class Doc(object):
    def __init__(self):
        self.doc_id = ''
        self.type_id = ''
        self.is_delete = '0'
        self.is_check = '0'
        self.file_name = ''
        self.is_train = '0'

        self.characters = []
        self.words = []
        self.sentences = []
        self.lines = []
        self.entities = []
        self.relations = []
        self.samples = []
        self.skip_sentence_relation = []
        self.multi_relation = []
        self.num_words = 0
        self.num_sentences = 0
        self.num_entities = 0
        self.num_relations = 0

    def lines2characters(self):  # 把line中的character 加到characters中
        index = 0
        for l in self.lines:
            l_texts = l.text
            line_id = l.id
            for w in l_texts:
                self.characters.append(Character(w, index, line_id))
                index += 1
            self.characters.append(Character("\n", index, line_id))
            index += 1
        if len(self.characters) > 0:  # 这里居然有0kb的文件
            self.characters.pop(-1)
        assert "\n".join(list(map(lambda x: x.text, self.lines))) == "".join(
            list(map(lambda x: x.text, self.characters)))


class Character(object):
    def __init__(self, text, pos, line_id):
        self.text = text
        self.pos = pos
        self.line_id = line_id
        self.label = ''
        self.predict_label = ''


class Word(object):
    def __init__(self, w_id, w_text, w_freq, w_sid, is_entity, belong2t_id, have_rela, ridtid):
        # id, is_entity, start_end_index, 每个单词在文档中出现了几次等等
        self.wordID = w_id
        self.word_text = w_text
        self.words_freq_in_doc = w_freq
        self.words_sentID = w_sid
        self.is_entity = is_entity
        self.belong2t_id = belong2t_id  # 属于哪个实体，该实体的id
        self.have_relation = have_rela
        self.ridtid = ridtid


class Sentence(object):
    def __init__(self, s_id, s_len, s_start2end_index, s_words_num, s_text):
        self.s_id = s_id
        self.s_len = s_len
        self.s_start2end_index = s_start2end_index
        self.s_words_num = s_words_num
        self.s_text = s_text
        self.entitys = []
        self.relations = []

    def init(self):
        self.s_entities_num = len(self.entitys)
        self.s_entities_id = list(map(lambda x: x.id, self.entitys))
        self.s_relations_num = len(self.relations)
        self.s_relations_id = list(map(lambda x: x.id, self.relations))
        pass


class Line(object):
    def __init__(self, line_id, doc_id, text):
        self.id = line_id
        self.doc_id = doc_id
        self.text = text


class Entity(object):
    def __eq__(self, another):
        if type(self) == type(another) and self.id == another.id:
            return True
        return False

    def __init__(self, id, text, pos, type, doc_id):
        self.id = id
        self.text = text
        self.pos = pos
        self.type = type
        self.doc_id = doc_id


class Relation(object):
    def __init__(self, r_id, r_type, e1, e2, e1_ty, e2_ty, m_r):
        self.id = r_id
        self.entity1_type = e1_ty
        self.entity2_type = e2_ty
        self.relation_type = r_type
        self.entity1 = e1
        self.entity2 = e2
        self.skip_sentence = 0
        self.multi_relation = m_r
        # sum(len(i.multi_relation) for doc_r in list(map(lambda x: x.relations, result)) for i in doc_r)


class Sample(object):
    def __init__(self):
        pass


class Vocab(object):
    def __init__(self):
        pass
