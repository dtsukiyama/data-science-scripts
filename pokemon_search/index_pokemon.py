
# PYTHONPATH=. luigi --module index_pokemon indexDocuments --local-scheduler

import luigi
import pandas as pd
import json
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import date
import index as i

class pokemonCards(luigi.Task):

    date = luigi.DateParameter(default=date.today())

    def output(self):
        return luigi.LocalTarget('data/' + 'all_cards_{}.json'.format(self.date))


    def run(self):
    
        pagesize = 500
        url = 'https://api.pokemontcg.io/v1/cards'
        response = requests.get(url, verify=True)
        jData = json.loads(response.content)

        def getCards(url, page, pagesize):
            api = url + '?page=' + str(page) + '&pageSize=' + str(pagesize)
            response = requests.get(api, verify=True)
            return json.loads(response.content)

        all_cards = []
        for i in range(1, 20, 1):
            cards = getCards(url, i, pagesize)['cards']
            all_cards = all_cards + cards 
            print 'Processing ' + str(i) + '...'
        
        with self.output().open('w') as outfile:
            json.dump(all_cards, outfile)
      

class indexDocuments(luigi.Task):

    today = date.today()
    date = luigi.DateParameter(default=today)
    
    def requires(self):
        return pokemonCards(self.date)

    def run(self):
  
        print "getting cards..."
        with open(self.input().fn) as data_file:
            data = json.load(data_file)
        print "done"

        with open('analysis_settings.json') as data_file:    
            analysis_settings = json.load(data_file)
        
        with open('mapping_settings.json') as data_file:    
            mapping_settings = json.load(data_file)
            
        print "indexing documents..."
        i.reindex(analysis_settings = analysis_settings, mapping_settings = mapping_settings, Dict=data,
                  index_name = "pokemon_cards", doc_type = "card", identifier = "index")

                
        print "finished indexing"

if __name__ == "__main__":
    luigi.run(['indexDocuments'])



