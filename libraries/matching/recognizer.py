from __future__ import unicode_literals, print_function

import pprint
import time
import itertools
import re

from spacy.lang.en import English
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
from spacy.tokens import Doc, Span, Token
from tqdm import tqdm

nlp = English()

entities = {'PERSON':'People, including fictional.',
            'NORP':'Nationalities or religious or political groups.',
            'FACILITY':'Buildings, airports, highways, bridges, etc.',
            'ORG':'Companies, agencies, institutions, etc.',
            'GPE':'Countries, cities, states.',
            'LOC':'Non-GPE locations, mountain ranges, bodies of water.',
            'PRODUCT':'Objects, vehicles, foods, etc. (Not services.)',
            'EVENT':'Named hurricanes, battles, wars, sports events, etc.',
            'WORK_OF_ART':'Titles of books, songs, etc.',
            'LAW':'Named documents made into laws.',
            'LANGUAGE':'Any named language.',
            'DATE':'Absolute or relative dates or periods.',
            'TIME':'Times smaller than a day.',
            'PERCENT':'Percentage, including "%".',
            'MONEY':'Monetary values, including unit.',
            'QUANTITY':'Measurements, as of weight or distance.',
            'ORDINAL':'first, second, etc.',
            'CARDINAL':'Numerals that do not fall under another type.'}

def removeNonAscii(data):
        return unicode("".join(i for i in data if ord(i)<128))

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
    
def view():
    pprint.pprint(entities)
    

class multipleMatch(object):
    def __init__(self):
        self.matcher = PhraseMatcher(nlp.vocab)
        
    def patterns(self, tokens):
        return [nlp(text) for text in tokens]
         
    def fit(self, label, patterns):
        return self.matcher.add(label, None, *patterns)
     
    def call(self, doc):
        return self.matcher(doc)
    
    def recall(self, text):
        doc = nlp(text)
        matches = self.call(doc)
        lookup = dict()
        for match_id, start, end in matches:
            rule_id = nlp.vocab.strings[match_id]
            span = doc[start : end]
            lookup[span.text] = rule_id
        return lookup
    
class phraseRecognizer(object):

    def __init__(self, phrases, label = 'PERSON', mylabel=None):
        """
        Args: list of phrases to match, entity label, redesignate label with custom label
        Returns: phrase matcher object
        
        Use: labels attach an entity type to matched phrases. However these entities must adhere to spaCy's entity types.
             You can designate your own label with mylabel, this simply creates a look-up table. 
             
        termMatcher ignore entity types; therefore this argument can be ignored. However spanMatcher will return entity type.
        
        # simply match all phrases
        pr = phraseRecognizer(naruto)
             
        # match all phrases or return phrases with entity type 'PERSON'     
        pr = phraseRecognizer(naruto, label='PERSON')
        
        # match all phrases and designate entity type 'PERSON' as 'ANIME'
        pr = phraseRecognizer(naruto, label='PERSON',mylabel='ANIME')
       
        """
        self.label = nlp.vocab.strings[label]
        self.entity = label
        patterns = [nlp(text) for text in phrases]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('myList', None, *patterns)   
        Token.set_extension('is_term', default=False, force=True)
        self.entity_table = {self.entity:mylabel}


    def termMatcher(self, text):
        """
        Args:  text we wish to match
        Returns: list of matched terms
        """
        terms = []
        doc = nlp(text)
        matches = self.matcher(doc)
        for ent_id, start, end in matches:
            terms.append(doc[start:end].text)
        return ', '.join([str(b) for b in terms])
    
    def uniqueTerms(self, text):
        """
        Args:  text we wish to match
        Returns: list of matched terms
        """
        terms = set()
        doc = nlp(text)
        matches = self.matcher(doc)
        for ent_id, start, end in matches:
            terms.add(doc[start:end].text)
        return ', '.join([str(b) for b in terms])  
    
    def spanMatcher(self, text):
        """
        From spaCy repository; attaches a label to entity. 
        """
        doc = nlp(text)
        matches = self.matcher(doc)
        spans = []  
        for _, start, end in matches:
            entity = Span(doc, start, end, label=self.label)
            spans.append(entity)
            for token in entity:
                token._.set('is_term', True)
            doc.ents = list(doc.ents) + [entity]
        for span in spans:
            span.merge()
            
        if not self.entity_table[self.entity]:
            return [(e.text, e.label_) for e in doc.ents]
        else:
            return [(e.text, self.entity_table[e.label_]) for e in doc.ents]  
        
        
class pipeRecognizer(object):

    def __init__(self, terms, label = 'SKILL', mylabel=None):
        """
        Args: list of phrases to match, entity label, redesignate label with custom label
        Returns: phrase matcher object
        
        Use: labels attach an entity type to matched phrases. However these entities must adhere to spaCy's entity types.
             You can designate your own label with mylabel, this simply creates a look-up table. 
             
        termMatcher ignore entity types; therefore this argument can be ignored. However spanMatcher will return entity type.
        
        # simply match all phrases
        pr = phraseRecognizer(naruto)
             
        # match all phrases or return phrases with entity type 'PERSON'     
        pr = phraseRecognizer(naruto, label='PERSON')
        
        # match all phrases and designate entity type 'PERSON' as 'ANIME'
        pr = phraseRecognizer(naruto, label='PERSON',mylabel='ANIME')
       
        """
        self.label = nlp.vocab.strings[label]
        self.entity = label
        patterns = [nlp(text) for text in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add('myList', None, *patterns)   
        Token.set_extension('is_term', default=False, force=True)
        self.entity_table = {self.entity:mylabel}
        
    def pipeMatcher(self, text):
        doc = nlp(text)
        terms = set()
        matches = self.matcher(doc)
        if matches:
            for ent_id, start, end in matches:
                terms.add(doc[start:end].text)
            return ", ".join([str(b) for b in terms])
        else:
            pass
        

    
class batchPipeRecognizer(object):
    
    def __init__(self, terms):
        
        self.patterns = self.buildPatterns(terms)
        self.matcher = self.buildMatcher(self.patterns)
            
            
    def tokenPattern(self, token):
        """
        Args: a term we wish to match
        Returns: skill formatted in the pattern we wish to match:
           - [{'LOWER': 'hello'}, {'IS_PUNCT': True}, {'LOWER': 'world'}]
        ATTRIBUTE                       DESCRIPTION
        ORTH                            The exact verbatim text of a token.
        LOWER                           The lowercase form of the token text.
        LENGTH                          The length of the token text.
        IS_ALPHA, IS_ASCII, IS_DIGIT    Token text consists of alphanumeric characters, ASCII characters, digits.
        IS_LOWER, IS_UPPER, IS_TITLE    Token text is in lowercase, uppercase, titlecase.
        IS_PUNCT, IS_SPACE, IS_STOP     Token is punctuation, whitespace, stop word.
        LIKE_NUM, LIKE_URL, LIKE_EMAIL  Token text resembles a number, URL, email.
        POS, TAG, DEP, LEMMA, SHAPE     The token's simple and extended part-of-speech tag, dependency label, lemma, shape.
        ENT_TYPE                        The token's entity label.
        """
        pattern = []
        for b in token.split():
            pattern.append({'ORTH':b})  
        return pattern

    def buildPatterns(self, tokens):
        """
        Args: takes in a list of terms we wish to match
        Returns: formats all terms in the list 
        """
        pattern = []
        for token in tokens:
            pattern.append(self.tokenPattern(token))
        return list(zip(tokens, pattern))


    def buildMatcher(self, patterns):
        """
        Args: formatted terms we wish to match
        Returns: spaCy Matcher object updated with of terms
        """
        matcher = Matcher(nlp.vocab)
        for pattern in patterns:
            matcher.add(pattern[0], None, pattern[1])
        return matcher

        
    def pipeMatcher(self, text):
        """
        Args: text we wish to match
        Returns: list of matched terms
        """
        doc = nlp(unicode(text))
        terms = set()
        matches = self.matcher(doc)
        if matches:
            for ent_id, start, end in matches:
                terms.add(doc[start:end].text)
            return ", ".join([str(b) for b in terms])
        else:
            pass   
        
        
    def createGenerators(self, text_tuples):
        gen1, gen2 = itertools.tee(text_tuples)
        ids = (id_ for (id_, text) in gen1)
        texts = (text for (id_, text) in gen2)
        return ids, texts


    def batchPipeline(self, ids, texts, batch_size, n_threads):
        for work_id, doc in zip(ids, nlp.pipe(texts, batch_size=batch_size, n_threads=n_threads)):
            match = self.pipeMatcher(doc)
            if match:
                yield {'work_id':work_id,
                       'matches':match}
            else:
                pass
            
    def writeGenerator(self, generator, path):
        with open(path, 'w') as f:
            for b in generator:
                f.write(str(b)+'\n')

    def timeBatch(self, text, size):
        ids, docs = self.createGenerators(text[:size])
        result = self.batchPipeline(ids, docs, int(size/10), -1)
        start = time.time()
        next(result)
        end = time.time()
        return end - start

