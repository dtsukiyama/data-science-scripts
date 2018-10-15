# spacy 1.9
from __future__ import unicode_literals, print_function

from pathlib import Path

import random
import os
import timeit

import spacy
from spacy.gold import GoldParse
from spacy.tagger import Tagger
from spacy.matcher import Matcher
from spacy.attrs import IS_PUNCT, LOWER

import re

import yaml
import pandas as pd
import helper
import requests
import json

from elasticsearch import Elasticsearch
from elasticsearch import helpers

nlp = spacy.load('en')
matcher = Matcher(nlp.vocab)

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
res = requests.get('http://localhost:9200')

def removeNonAscii(data):
        return "".join(i for i in data if ord(i)<128)

def preprocessor(text):
    """
    Args: text field
    Returns: cleaned text
    """
    text = re.sub('<[^>]*>', ' ', text)
    text = re.sub('&nbsp;', ' ', text)
    text = re.sub('&amp;', ' ', text)
    text = re.sub('&gt;', ' ', text)
    emoticons = re.findall('(?::|;|=)(?:-)?(?:\)|\(|D|P)', text)
    text = re.sub('[\W]+', ' ', text.lower()) + ' '.join(emoticons).replace('-', ' ')
    return text

def skillSearch(query, verify=True):
    res = es.search(index="ner",
                    size=100, 
                    body={'query': {'match_phrase': { 'sentences': query, 
                                                }
                                }}
            )
    hits = res['hits']['total']
    if not verify:
        return hits
    else:
        print("Query: {}. Assignments this terms shows up in: {}".format(query, hits))
        
    
def skillVerify(skills):
    counts = []
    for skill in skills:
        counts.append(skillSearch(removeNonAscii(skill), verify=False))
    verified = list(zip(skills, counts))
    return [b[0] for b in verified if b[1] >= 5]

def text_highlights(query, samples = 500):
    """
    Args: search query and number of results
    Returns: clean lower cased sentences
    """
    res = es.search(index="ner",
                    size=samples, 
                    body={'query': {'match_phrase': { 'sentences': query, 
                                                }
                                }}
            )
    res = [b['_source']['sentences'] for b in res['hits']['hits']]
    res = [b.lstrip().lower() for b in res]
    return res
    
def annotate_training(sentences, skill, name):
    """
    Args: clean lower cased sentences, skills, entity category
    Returns: list of annotated sentences
    """
    train = []
    for sentence in sentences:
        train.append([(int(sentence.index(skill)), int(sentence.index(skill) + len(skill)), name)])
    return zip(sentences, train)
    

def create_training(sentences, skills):
    """
    Args: sentences from create_all_corpus
    Returns: annotated sentences for use in ner training
    """
    train = []
    for b in range(len(skills)):
        print("Index: {}. Skill: {}".format(b, skills[b]))
        train.extend(annotate_training(sentences[b], skills[b], 'SKILL'))
        
    return train


def create_all_corpus(skill_counts, curated = False, samples = 10):
    """
    Args: skills or skill_counts tuples, curated boolean
    Returns: list of sentences from search query
    """
    sentences = []
    if curated == False:
        for skill in skill_counts:
            sentences.append(text_highlights(skill[0]))
        return sentences
    else:
        for skill in skill_counts:
            sentences.append(text_highlights(skill, samples=samples))
        return sentences
    
    
def train_ner(nlp, train_data, model_name):
    # Add new words to vocab
    for raw_text, _ in train_data:
        doc = nlp.make_doc(raw_text)
        for word in doc:
            _ = nlp.vocab[word.orth]
    random.seed(0)
    # You may need to change the learning rate.
    nlp.entity.model.learn_rate = 0.001
    for itn in range(100):
        print("iteration: {}".format(itn))
        start = timeit.default_timer()
        random.shuffle(train_data)
        loss = 0.
        for raw_text, entity_offsets in train_data:
            doc = nlp.make_doc(raw_text)
            gold = GoldParse(doc, entities=entity_offsets)
            nlp.tagger(doc)
            loss += nlp.entity.update(doc, gold, drop=0.5)
        if loss == 0:
            break
        print(loss)
        end = timeit.default_timer()-start
        print("Iteration {} complete in {} minutes".format(itn, end/60))
    nlp.end_training()
    if output_dir:
        if not os.path.exists(model_name):
            os.makedirs(model_name)
        nlp.save_to_directory(model_name)
        
#-------------------------------- skill matching


def skillPattern(skill):
    """
    Args: a term we wish to match
    Returns: skill formatted in the pattern we wish to match:
       - [{'LOWER': 'hello'}, {'IS_PUNCT': True}, {'LOWER': 'world'}]
    """
    pattern = []
    for b in skill.split():
        pattern.append({'LOWER':b})  
    return pattern

def buildPatterns(skills):
    """
    Args: takes in a list of terms we wish to match
    Returns: formats all terms in the list 
    """
    pattern = []
    for skill in skills:
        pattern.append(skillPattern(skill))
    return list(zip(skills, pattern))

def buildMatcher(patterns):
    """
    Args: formatted terms we wish to match
    Returns: spaCy Matcher object updated with of terms
    """
    matcher = Matcher(nlp.vocab)
    for pattern in patterns:
        matcher.add_pattern(pattern[0], pattern[1])
    return matcher

def skillMatcher(matcher, text):
    """
    Args: our matcher, text we wish to match
    Returns: list of matched terms
    """
    skills = []
    doc = nlp(unicode(text.lower()))
    matches = matcher(doc)
    for b in matches:
        match_id, _, start, end = b
        skills.append(doc[start : end])
    return list(set([str(b) for b in skills]))
