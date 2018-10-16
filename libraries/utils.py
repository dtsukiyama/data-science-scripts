import os, errno
import re
import docker
import yaml
import numpy as np
import re
import json
import pickle
from contextlib import contextmanager


@contextmanager
def changeDirectory(newdir):
    """
    Credit goes here: https://stackoverflow.com/questions/431684/how-do-i-change-directory-cd-in-python/24176022#24176022
    Context manager is the best way to be pythonically safe 
    """
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)


def dirWalk(target):
    return next(os.walk(target))[1]


def modelChoice():
    try:
        os.makedirs('models')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    current_dir = os.getcwd()
    target = current_dir + "/" + 'models'
    return dirWalk(target)


def stringExtract(string):
    return re.findall(r"'(.*?)'", string, re.DOTALL)


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


def listdocker():
    client = docker.from_env()
    images = []
    for b in client.images.list():
        images.extend(stringExtract(str(b)))
    return [image for image in images if 'amazonaws' in image]



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


def resetMultiIndex(df):
    df.columns = df.columns.map('_'.join)
    return df


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = str('percentile_%s' % n)
    return percentile_

def buildLookupTable(df):
    lookup_table = dict()
    for index, row in df.iterrows():
        lookup_table[row['skills_']] = {'price_range': str(row['per_hour_price_percentile_5']) \
                                        + "-" + str(row['per_hour_price_percentile_95']),
                                        'observations': row['work_id_count']}
    return lookup_table


def pickleRead(input_file):
    with open (input_file, 'rb') as fp:
        file = pickle.load(fp)
    return file

