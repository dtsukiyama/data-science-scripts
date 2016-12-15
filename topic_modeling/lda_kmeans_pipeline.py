# PYTHONPATH=. luigi --module lda_and_cluster cluster_companies --local-scheduler


#!/usr/bin/python2
import luigi
import yaml
import pandas.io.sql as sql
import pandas as pd
import numpy as np
import pymysql
import pyprind
import json
from lda import t_model
from sklearn.cluster import KMeans
from sklearn import preprocessing


cfg = yaml.load(open('database_configurations.yaml', 'r'))['production']

class classify_jobs(luigi.Task):
   
    def output(self):
        return luigi.LocalTarget('data/classified_jobs.csv')

    def run(self):
    
        def get_data(file_name):
            conn = pymysql.connect(database = cfg['database'],
                                       user = cfg['user'],
                                   password = cfg['password'],
                                       host = cfg['host'],
                                       port = cfg['port'])
            with open('sql/'+ file_name + '.sql', 'r') as queryfile:
                user_query=queryfile.read().replace('\n', ' ')
            data = sql.read_sql(user_query, conn)
            return data
            conn.close()
            
        def clean_data(data):
            data['topic'] = data['topic'].fillna(100)
            data['topic'] = data['topic'].astype(int)
            data['state'] = data['state'].fillna(1000)
            data['state'] = data['state'].astype(int)
            data['industry_id'] = data['industry_id'].fillna(0)
            data['industry_id'] = data['industry_id'].astype(int)
            return data
        
        data = get_data('work_titles')
        
        with open('data/lda_training.txt', 'rU') as in_file:
            train = in_file.read().split('\n')
            
        tm = t_model(100)
        sample_model = tm.load_model('lda.model')
        print "creating corpus and word count dictionary..."
        word_count_dict, bag_of_words_corpus = tm.bag_of_words(train)
        print "done"
        
        print "test classifier..."
        unseen_document = 'example document'
        tm.classify(word_count_dict, sample_model, unseen_document)
        print "done"
        
        print "classify jobs..."
        topics = []
        pbar = pyprind.ProgBar(len(data))
        for b in data['title'].values:
            topics.append(tm.classify(word_count_dict,sample_model,b))
            pbar.update()
        data['topic'] = topics
        data = clean_data(data)
        data.dropna().to_csv(self.output().fn, sep=',', index=False)
        
class cluster_companies(luigi.Task):

    def output(self):
        return luigi.LocalTarget('data/clustered_companies.csv')

    def requires(self):
        return classify_jobs()
        
    def run(self):
    
        def process_data(data):
            data.loc[data['price']==0, 'price']=0.1
            data['price'] = np.log(data['price'])
            le = preprocessing.LabelEncoder()
            data[['industry_id','state','topic']] = data[['industry_id','state','topic']].apply(le.fit_transform)
            return data
            
        data = pd.read_csv(self.input().fn)
        data = process_data(data)
        X = data[['industry_id','price','state','topic']].values
        num_cluster = 4
        print "clustering data..."
        km = KMeans(n_clusters = num_cluster)
        km.fit(X)
        print "done"
        data['clusters'] = km.labels_.tolist()
        print "exporting data..."
        data.to_csv(self.output().fn, sep=',', index=False)
        print "done"
        

if __name__ == "__main__":
    luigi.run(['cluster_companies'])
        
