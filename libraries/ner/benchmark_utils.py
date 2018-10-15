from __future__ import unicode_literals, print_function

from pathlib import Path

import random
import os
import timeit
import pandas as pd
import numpy as np

import spacy
from spacy.gold import GoldParse
from spacy.tagger import Tagger

import re
from collections import OrderedDict
from ner_utils_stable import preprocessor, removeNonAscii

import yaml
import helper
import requests
import json

import nltk
from nltk import word_tokenize
from nltk.util import ngrams

# load our trained NER
nlp = spacy.load('en', path='alpha_model')
nlp.entity.add_label('SKILL')

with open('verified_skills.txt','r') as f:
    skills_library = f.read().splitlines()

def get_skill(document):
    """
    Args: spaCy tagged document
    Returns: words from document where entity type is SKILL
    """
    return [word.text for word in document if word.ent_type_ == "SKILL"]

def create_ngrams(text):
    """
    Args: text
    Returns: list of bigrams and trigrams
    """
    token=nltk.word_tokenize(text)
    trigrams = [' '.join(b) for b in ngrams(token,3)]
    bigrams = [' '.join(b) for b in ngrams(token,2)]
    return trigrams + bigrams
    

def skill_keyword_validator(document):
    document = nlp(unicode(preprocessor(document)))
    keywords = get_skill(document)
    return [b for b in keywords if b in skills_library]


def skill_phrase_validator(document):
    document = nlp(unicode(preprocessor(document)))
    ngrams = [b for b in create_ngrams(' '.join(get_skill(document))) if b in skills_library]
    return ngrams


def validate_keywords(data):
    """
    Args: original text data, spaCy nlp, trained ner model
    Returns: returns list of entities and ngram entities validated against skills list
    """
    validated = []
    start = timeit.default_timer()
    for b in data:
        validated.append(skill_keyword_validator(b.lower()))
        
    end = timeit.default_timer()-start
    print("Validation complete with time {} minutes".format(end/60))
    
    return [list(OrderedDict.fromkeys(b)) for b in validated]


def validate_phrases(data):
    """
    Args: original text data, spaCy nlp, trained ner model
    Returns: returns list of entities and ngram entities validated against skills list
    """
    validated = []
    start = timeit.default_timer()

    for b in data:
        validated.append(skill_phrase_validator(b.lower()))
        
    end = timeit.default_timer()-start
    print("Validation complete with time {} minutes".format(end/60))
    return [list(OrderedDict.fromkeys(b)) for b in validated]

def removeNonKeywords(keywords, phrases):
    notlist = []
    filtered = []
    last = []
    for a, b in zip(keywords, phrases):
        notlist.append(' '.join(set(create_ngrams(' '.join(a))).intersection(set(b))).split())
    for a, b in zip(keywords, notlist):
        filtered.append(list(set(a).difference(set(b))))
    for a, b in zip(filtered, phrases):
        last.append(list(set(a).union(set(b))))
    return last

