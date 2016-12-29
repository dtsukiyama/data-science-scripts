from flask import Flask
from flask import request
from flask import render_template
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import pandas as pd
import numpy as np
import re

host = "http://localhost:9200"
es = Elasticsearch(host)

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template("pokemon_search.html")
    
def extract_source(data):
    source = []
    for hit in data:
        source.append(hit['_source'])
        if len(source) == len(data):
            return source
        else:
            pass

@app.route('/', methods=['POST'])           
def card_results():
    query = request.form['pokemon']
    results = es.search(index=["pokemon_cards"],
                body={'query': {'multi_match': { 'query': query, 
                                                 'fuzziness': 'AUTO',
                                                 'fields': ['name']
                                                }
                                },
                                'size': 100
                           })
    return render_template('pokemon_results.html', results = results)
    
if __name__ == '__main__':
    app.run(debug=True)
