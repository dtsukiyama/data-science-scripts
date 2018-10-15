import yaml
import pandas as pd
import helper
import requests
import json
import re

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

res = requests.get('http://localhost:9200')
print(res.content)

mappingSettings = {
       "job": {
            "properties": {
                "id": {"type": "string"},  
            
                "sentences": {"type":"string",
                              "analyzer": "english_bigrams",
                              "fields": {
                                   "suggest":{"type":"completion"},
                    
                                   "bigrammed": {
                                     "type": "string",
                                     "analyzer": "english_bigrams"}}}

                    }
                }       
            }


            
analysisSettings = {
   "analyzer" : {
      "default": {
        "type": "english"
      },
      "english_bigrams": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "standard",
            "lowercase",
            "bigram_filter"
          ]
      },
      "shingler":{
          "type":"custom",
          "tokenizer":"standard",
          "filter":["lowercase","shingle"]
        }  
        
    },
   "filter": {
     "bigram_filter": {
         "type": "shingle",
         "max_shingle_size": 3,
         "min_shingle_size": 2
     }}}




def preprocessor(text):
    """ use to clean up text column: data['col'] = data['col'].apply(preprocessor) """
    text = re.sub('<[^>]*>', ' ', text)
    text = re.sub('&nbsp;', ' ', text)
    text = re.sub('&amp;', ' ', text)
    text = re.sub('&gt;', ' ', text)
    text = re.sub("[^a-zA-Z-.]", " ", text).replace('-', ' ')
    return text


def batch_index(dictionary, batch_size):
    batch_size = batch_size
    num_batches = len(dictionary)/batch_size
    if len(dictionary)%batch_size != 0:
        #then there's an additional partial batch to account for
        num_batches += 1  
    return num_batches
    

    
def create_batches(dictionary, batch_size):
    num_batches = batch_index(dictionary, batch_size)
    batches = []
    for batch_num in xrange(num_batches):
        docs = dictionary[batch_num*batch_size:(batch_num+1)*batch_size]
        json_docs = []
        for doc in docs:
            doc_short = {}
            doc_short["sentences"] = doc["sentences"]
            doc_short['id'] = doc['id']
            addCmd = {"index": {"_index": "ner", "_type": "sentence", "_id": doc_short["id"]}}
            json_docs.append(json.dumps(addCmd))
            json_docs.append(json.dumps(doc_short))
        batches.append("\n".join(json_docs)+"\n")
    return batches



def batch_reindex(batch_size, analysisSettings={}, mappingSettings={}, Dict={}, index_name = "index_name"):
    
    elasticSearchUrl = "http://localhost:9200"
    batches = create_batches(Dict, batch_size)
    settings = { 
        "settings": {
            "number_of_shards": 1, 
            "index": {
                "analysis" : analysisSettings, 
            }}}

    if mappingSettings:
        settings['mappings'] = mappingSettings 

    resp = requests.delete("http://localhost:9200/" + str(index_name)) 
    resp = requests.put("http://localhost:9200/" + str(index_name), data=json.dumps(settings))
    print("batch indexing...")
    for batch in batches:
        resp = requests.post(elasticSearchUrl + "/_bulk", data=batch)
    print("done")
    
    
import yaml
import pandas as pd
import helper
import requests
import json
import re

from elasticsearch import Elasticsearch
from elasticsearch import helpers

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

res = requests.get('http://localhost:9200')
print(res.content)

mappingSettings = {
       "job": {
            "properties": {
                "id": {"type": "string"},  
            
                "sentences": {"type":"string",
                              "analyzer": "english_bigrams",
                              "fields": {
                                   "suggest":{"type":"completion"},
                    
                                   "bigrammed": {
                                     "type": "string",
                                     "analyzer": "english_bigrams"}}}

                    }
                }       
            }


            
analysisSettings = {
   "analyzer" : {
      "default": {
        "type": "english"
      },
      "english_bigrams": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "standard",
            "lowercase",
            "bigram_filter"
          ]
      },
      "shingler":{
          "type":"custom",
          "tokenizer":"standard",
          "filter":["lowercase","shingle"]
        }  
        
    },
   "filter": {
     "bigram_filter": {
         "type": "shingle",
         "max_shingle_size": 3,
         "min_shingle_size": 2
     }}}




def preprocessor(text):
    """ use to clean up text column: data['col'] = data['col'].apply(preprocessor) """
    text = re.sub('<[^>]*>', ' ', text)
    text = re.sub('&nbsp;', ' ', text)
    text = re.sub('&amp;', ' ', text)
    text = re.sub('&gt;', ' ', text)
    text = re.sub("[^a-zA-Z-.]", " ", text).replace('-', ' ')
    return text


def batch_index(dictionary, batch_size):
    batch_size = batch_size
    num_batches = len(dictionary)/batch_size
    if len(dictionary)%batch_size != 0:
        #then there's an additional partial batch to account for
        num_batches += 1  
    return num_batches
    

    
def create_batches(dictionary, batch_size):
    num_batches = batch_index(dictionary, batch_size)
    batches = []
    for batch_num in xrange(num_batches):
        docs = dictionary[batch_num*batch_size:(batch_num+1)*batch_size]
        json_docs = []
        for doc in docs:
            doc_short = {}
            doc_short["sentences"] = doc["sentences"]
            doc_short['id'] = doc['id']
            addCmd = {"index": {"_index": "ner", "_type": "sentence", "_id": doc_short["id"]}}
            json_docs.append(json.dumps(addCmd))
            json_docs.append(json.dumps(doc_short))
        batches.append("\n".join(json_docs)+"\n")
    return batches



def batch_reindex(batch_size, analysisSettings={}, mappingSettings={}, Dict={}, index_name = "index_name"):
    
    elasticSearchUrl = "http://localhost:9200"
    batches = create_batches(Dict, batch_size)
    settings = { 
        "settings": {
            "number_of_shards": 1, 
            "index": {
                "analysis" : analysisSettings, 
            }}}

    if mappingSettings:
        settings['mappings'] = mappingSettings 

    resp = requests.delete("http://localhost:9200/" + str(index_name)) 
    resp = requests.put("http://localhost:9200/" + str(index_name), data=json.dumps(settings))
    print("batch indexing...")
    for batch in batches:
        resp = requests.post(elasticSearchUrl + "/_bulk", data=batch)
    print("done")
    
    
def main(index_name):
    print("pulling assignment text data...")
    data = helper.getData('descriptions')
    print("done")
    
    print("processing data...")
    data['description'] = [str(b) for b in data['description']]
    data['description_text'] = data['description'].apply(preprocessor)
    data['description_text'] = [' '.join(b.split()) for b in data['description_text']]
    
    sentences = (' '.join(data['description_text'])).lower().split('.')
    sentences = filter(None, sentences)
    sentences = list(set(sentences))
    sentences = [b.lstrip() for b in sentences]
    print("done")
    
    df = pd.DataFrame({'sentences':sentences}).reset_index().rename(columns={'index':'id'})
    df = json.loads(df.to_json(orient='records'))
    batch_reindex(10000, analysisSettings=analysisSettings, mappingSettings=mappingSettings, Dict = df, index_name = index_name)
    print("finished indexing training sentences")
    
if __name__ == '__main__':
    import plac
    plac.call(main)
def main(index_name):
    print("pulling assignment text data...")
    data = helper.getData('descriptions')
    print("done")
    
    print("processing data...")
    data['description'] = [str(b) for b in data['description']]
    data['description_text'] = data['description'].apply(preprocessor)
    data['description_text'] = [' '.join(b.split()) for b in data['description_text']]
    
    sentences = (' '.join(data['description_text'])).lower().split('.')
    sentences = filter(None, sentences)
    sentences = list(set(sentences))
    sentences = [b.lstrip() for b in sentences]
    print("done")
    
    df = pd.DataFrame({'sentences':sentences}).reset_index().rename(columns={'index':'id'})
    df = json.loads(df.to_json(orient='records'))
    batch_reindex(10000, analysisSettings=analysisSettings, mappingSettings=mappingSettings, Dict = df, index_name = index_name)
    print("finished indexing training sentences")
    
if __name__ == '__main__':
    import plac
    plac.call(main)

