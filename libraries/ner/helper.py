from __future__ import division

import re
import numpy as np
import pandas as pd
import json
import random
import os
from collections import Counter

import MySQLdb
import pandas.io.sql as sql
import yaml


cfg = yaml.load(open('configuration.yaml', 'r'))['prod']


def getData(file_name):
    conn = MySQLdb.connect(cfg['host'], 
                           cfg['user'], 
                           cfg['password'], 
                           cfg['database'],
                           ssl= cfg['cipher'])
    with open('sql/'+ file_name + '.sql', 'r') as queryfile:
        user_query=queryfile.read().replace('\n', ' ')
        data = sql.read_sql(user_query, conn)
        return data
        conn.close()
        

def get_target(words, idx, window_size=5):
    ''' Get a list of words in a window around an index. '''
    
    R = np.random.randint(1, window_size+1)
    start = idx - R if (idx - R) > 0 else 0
    stop = idx + R
    target_words = set(words[start:idx] + words[idx+1:stop+1])
    
    return list(target_words)


def get_batches(int_text, batch_size, seq_length):
    """
    Return batches of input and target
    :param int_text: Text with the words replaced by their ids
    :param batch_size: The size of batch
    :param seq_length: The length of sequence
    :return: A list where each item is a tuple of (batch of input, batch of target).
    """
    n_batches = int(len(int_text) / (batch_size * seq_length))

    # Drop the last few characters to make only full batches
    xdata = np.array(int_text[: n_batches * batch_size * seq_length])
    ydata = np.array(int_text[1: n_batches * batch_size * seq_length + 1])

    x_batches = np.split(xdata.reshape(batch_size, -1), n_batches, 1)
    y_batches = np.split(ydata.reshape(batch_size, -1), n_batches, 1)

    return list(zip(x_batches, y_batches))


def create_lookup_tables(words):
    """
    Create lookup tables for vocabulary
    :param words: Input list of words
    :return: A tuple of dicts.  The first dict....
    """
    word_counts = Counter(words)
    sorted_vocab = sorted(word_counts, key=word_counts.get, reverse=True)
    int_to_vocab = {ii: word for ii, word in enumerate(sorted_vocab)}
    vocab_to_int = {word: ii for ii, word in int_to_vocab.items()}

    return vocab_to_int, int_to_vocab

def get_batches(words, batch_size, window_size=5):
    ''' Create a generator of word batches as a tuple (inputs, targets) '''
    
    n_batches = len(words)//batch_size
    
    # only full batches
    words = words[:n_batches*batch_size]
    
    for idx in range(0, len(words), batch_size):
        x, y = [], []
        batch = words[idx:idx+batch_size]
        for ii in range(len(batch)):
            batch_x = batch[ii]
            batch_y = get_target(batch, ii, window_size)
            y.extend(batch_y)
            x.extend([batch_x]*len(batch_y))
        yield x, y
        
def lookup_and_config(input_dir, n_embedding=300, n_sampled=100, valid_size=10, valid_window=100):
    """
    Args: path to skills data, number of embeddings, number sampled, validation size, and validation window
    Returns: configurations for word2bvec trainings and lookup tables
    """
    if not os.path.exists(input_dir):
        print("make sure you have a skills dataset")
    
    with open(input_dir,'r') as f:
        skills = f.read().splitlines()
    
    vocab_to_int, int_to_vocab = create_lookup_tables(skills)
    int_words = [vocab_to_int[word] for word in skills]
    
    threshold = 1e-5
    word_counts = Counter(int_words)
    total_count = len(int_words)
    freqs = {word: count/total_count for word, count in word_counts.items()}
    p_drop = {word: 1 - np.sqrt(threshold/freqs[word]) for word in word_counts}
    train_words = [word for word in int_words if p_drop[word] < random.random()]

    if not os.path.exists("data"):
        os.makedirs("data")
    
    json.dump(int_to_vocab, open("data/int_to_vocab.txt",'w'))
    json.dump(vocab_to_int, open("data/vocab_to_int.txt",'w'))
    
    config = {'threshold': threshold,
              'word_counts': word_counts,
              'total_count': total_count,
              'freqs': freqs,
              'p_drop': p_drop,
              'train_words': train_words,
              'n_vocab': len(int_to_vocab),
              'n_embedding': n_embedding,
              'n_sampled': n_sampled,
              'valid_size': valid_size,
              'valid_window': valid_window}
    
    return config, vocab_to_int, int_to_vocab

def mostSimilar(features, id , N):
    """
    Args: Embedding matrix from word2vec, id of skill from vocab_to_int lookup table, number of similar skills to return
    Returns: Top N similar skills
    """
    norms = np.linalg.norm(features, axis = -1)
    factors = features / norms[:, np.newaxis]
    score = factors.dot(factors[id])
    candidates = [b for b in np.argpartition(score, -N)[-N:] if b != id]
    # int idx to vocab
    candidates = [' '.join(int_to_vocab[b].split()) for b in candidates]
    return candidates
