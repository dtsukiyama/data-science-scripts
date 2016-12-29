        
import json
import requests   
        
def batch_index(dictionary, batch_size):
    batch_size = batch_size
    num_batches = len(dictionary)/batch_size
    if len(df)%batch_size != 0:
        num_batches += 1  
    return num_batches
    
def create_batches(dictionary):
    num_batches = batch_index(dictionary, 50000)
    batches = []
    for batch_num in xrange(num_batches):
        docs = dictionary[batch_num*batch_size:(batch_num+1)*batch_size]
        json_docs = []
        for doc in docs:
            doc_short = {}
            doc_short["url"] = doc["url"]
            doc_short["name"] = doc["name"]
            doc_short['id'] = doc['id']
            addCmd = {"index": {"_index": "pokemon_cards", "_type": "card", "_id": doc_short["id"]}}
            json_docs.append(json.dumps(addCmd))
            json_docs.append(json.dumps(doc_short))
        batches.append("\n".join(json_docs)+"\n")
    return batches

def batch_reindex(analysisSettings={}, mappingSettings={}, Dict={}, index_name = "index_name"):
    
    elasticSearchUrl = "http://localhost:9200"
    batches = create_batches(Dict)
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
    print "batch indexing..."
    for batch in batches:
        resp = requests.post(elasticSearchUrl + "/_bulk", data=batch)
    print "done"        
        
def reindex(analysisSettings={}, mappingSettings={}, Dict={}, index_name = "index_name", doc_type = "doc_type", identifier = "identifier"):
    settings = { 
        "settings": {
            "number_of_shards": 1, 
            "index": {
                "analysis" : analysisSettings, 
            }}}

    if mappingSettings:
        settings['mappings'] = mappingSettings 

    resp = requests.delete("http://localhost:9200/" + str(index_name)) 
    resp = requests.put("http://localhost:9200/" + str(index_name), 
                        data=json.dumps(settings))

    bulk_upload = ""
    print "building..."
    for id, data in Dict.iteritems(): 
        addCmd = {"index": {"_index": str(index_name), 
                            "_type": str(doc_type),
                            "_id": data[str(identifier)]}}
        bulk_upload += json.dumps(addCmd) + "\n" + json.dumps(data) + "\n"

    print "indexing..."
    resp = requests.post("http://localhost:9200/_bulk", data=bulk_upload)
    

