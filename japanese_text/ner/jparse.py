#!/usr/bin/env python
# -*- coding: utf-8 -*- 


import MeCab

tagger = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd/")

entity_dict = {'LOC':'地域',
               'ORG':'組織',
               'PERSON':'人名'}
               
def tokenize(text):
    """
    Args: raw text and tagger
    Returns: tokenized Japanese text
    """
    parsed = tagger.parseToNode(text)
    components = []
    while parsed:
        components.append(parsed.surface)
        parsed = parsed.next
    return [b for b in components if b]
    
def entity_loc(components, ENTITY):
    """
    Args: tokenized Japanese text
    Returns: tokens which correspond to specific entity type
    """
    entities = [tagger.parse(b).split(',')[2] for b in components]
    return [b[0] for b in zip(components, entities) if b[1] == entity_dict[ENTITY]]
    
def get_ent(text, ent_type=False):
    """
    Args: raw Japanese text, ent_type which if True returns tuple with token and entity type
    Returns: all entities
    """
    components = tokenize(text)
    entities = [tagger.parse(b).split(',')[2] for b in components]
    if ent_type:
        return [b for b in zip(components,entities) if b[1] == '地域' or b[1] =='組織' or b[1] =='人名']
    else:
        return [b[0] for b in zip(components,entities) if b[1] == '地域' or b[1] =='組織' or b[1] =='人名']
    
    