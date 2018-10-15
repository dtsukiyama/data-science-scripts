from __future__ import unicode_literals, print_function

import yaml
import pandas as pd
import helper
import requests
import json
import re
import spacy
import timeit

from ner_utils_stable import skillSearch, skillVerify, create_all_corpus, create_training, train_ner, removeNonAscii, preprocessor

with open('stopwords.txt','r') as f:
    stop_words = f.read().splitlines()

def main(samples):
    
    # pull skills from user skill associations 
    skills = helper.getData('skills')
    verified_skills = skillVerify(skills['skill'].values)
    
    # clean up verified skills
    verified_skills = [removeNonAscii(b.lower()) for b in verified_skills]
    verified_skills = [preprocessor(b) for b in verified_skills]
    verified_skills = [b.strip() for b in verified_skills]
    verified_skills = [b for b in verified_skills if b not in stop_words]
    
    # export verified skills
    skillfile = open('verified_skills.txt', 'w')
    for skill in verified_skills:
        skillfile.write("%s\n" % skill)
    
    # annotate training sentences
    sentences = create_all_corpus(verified_skills, curated = True, samples = samples)
    train = create_training(sentences, verified_skills)
    
    start = timeit.default_timer()
    print("training ner...")
    nlp = spacy.load('en')
    nlp.entity.add_label('SKILL')
    train_ner(nlp, train, 'alpha_model')
    print("done")
    end = timeit.default_timer()-start
    print("Ner training complete in {} minutes".format(end/60))
    
if __name__ == '__main__':
    import plac
    plac.call(main)
    

