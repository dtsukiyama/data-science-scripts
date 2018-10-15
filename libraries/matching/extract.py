from __future__ import unicode_literals

import json
import pickle

from recognizer import pipeRecognizer
from recognizer import phraseRecognizer, removeNonAscii

with open ('data/skills', 'rb') as fp:
    skills = pickle.load(fp)

pr = pipeRecognizer(skills, mylabel='SKILL')

def lambda_handler(event, content):    
    p = event['queryStringParameters']['text']
    matches = pr.pipeMatcher(unicode(p))
    result = 'Skills ' + str(matches)
    return {'statusCode':200,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps({'skills':result})}
