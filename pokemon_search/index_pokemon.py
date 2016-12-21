
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
        return luigi.LocalTarget('data/' + 'all_cards_{}.csv'.format(self.date))


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
        
        data = pd.DataFrame([[b['imageUrl'],b['name']] for b in all_cards]).rename(columns={0:'url',1:'name'})
        data['id'] = data.index
        data.to_csv(self.output().fn, sep=',', index=False, encoding='utf-8')
      

class indexDocuments(luigi.Task):

    date = luigi.DateParameter(default=date.today())
    
    def requires(self):
        return pokemonCards(self.date)

    def run(self):
  
        print "getting cards..."
        data = pd.read_csv(self.input().fn)
        data = json.loads(data.reset_index().reset_index(drop=True).to_json(orient='index'))
        #data = json.loads(data.to_json(orient='index'))
        print "done"

        with open('analysis_settings.json') as data_file:    
            analysisSettings = json.load(data_file)
        
        with open('mapping_settings.json') as data_file:    
            mappingSettings = json.load(data_file)
            
        print "indexing documents..."
        i.reindex(analysisSettings = analysisSettings, mappingSettings = mappingSettings, Dict=data,
                  index_name = "pokemon_cards", doc_type = "card", identifier = "index")

                
        print "finished indexing"

if __name__ == "__main__":
    luigi.run(['indexDocuments'])



