import numpy as np
import pandas as pd
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer

class t_model(object):

    def __init__(self, num_topics = 100):
        self.num_topics = num_topics

    def lemmatize_and_stem(self, text):
        lm = WordNetLemmatizer()
        stemmer = SnowballStemmer("english")
        return stemmer.stem(lm.lemmatize(text, pos='v'))

    def tokenize_lemmatize(self, text):
        return [self.lemmatize_and_stem(token)
                for token in gensim.utils.simple_preprocess(text) 
                if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3]

    def bag_of_words(self, text):
        processed_docs = [self.tokenize_lemmatize(doc) for doc in text]
        word_count_dict = gensim.corpora.Dictionary(processed_docs)
        word_count_dict.filter_extremes(no_below=20, no_above=0.2)
        bag_of_words_corpus = [word_count_dict.doc2bow(pdoc) for pdoc in processed_docs]
        return word_count_dict, bag_of_words_corpus

    def lda_model(self, corpus, word_count_dictionary):
        print "this may take some time, depending on how large the set of documents are and number of topics..."
        lda_model = gensim.models.LdaMulticore(corpus, num_topics=self.num_topics, id2word=word_count_dictionary,
                                               passes=50, workers=4)
        print "done"
        return lda_model
            
            
    def topics(self, model):
        for idx, topic in model.print_topics(-1):
            print "Topic:{} Word composition:{}".format(idx, topic)
    
    def get_topics(self, model):
        index = range(0,self.num_topics,1)
        columns = ['word_composition']
        topics = []
        for idx, topic in model.print_topics(-1):
            topics.append(topic)
        data = pd.DataFrame(topics, index=index, columns=columns)
        data = data.reset_index().rename(columns={'index':'topic'})
        return data
    
    def score(self, model, document):
        bow_vector = word_count_dict.doc2bow(self.tokenize_lemmatize(document))
        for index, score in sorted(model[bow_vector], key=lambda tup: -1*tup[1]):
             print "Score: {}\t Topic: {}".format(score, model.print_topic(index, 5))
             
    def metrics(self, model, bag_of_word_corpus):
        print "perplexity of the model is", np.exp(model.log_perplexity(bag_of_words_corpus))
            
    def classify(self, dictionary, model, document):
        bow_vector = dictionary.doc2bow(self.tokenize_lemmatize(document))
        if not sorted(model[bow_vector], key=lambda tup: -1*tup[1]):
            #print "insufficient data to classify"
            return np.nan
        else:
            #print "score: {}".format(sorted(model[bow_vector], key=lambda tup: -1*tup[1])[0][1])
            #print "topic number: {}".format(sorted(model[bow_vector], key=lambda tup: -1*tup[1])[0][0])
            #print "returning topic number"
            return sorted(model[bow_vector], key=lambda tup: -1*tup[1])[0][0]
        
    def persist_model(self, path, model):
        print "saving model..."
        model.save(path)
        print "done"
        
    def load_model(self, path):
        return gensim.models.LdaModel.load(path)
