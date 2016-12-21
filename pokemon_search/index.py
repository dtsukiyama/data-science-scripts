        
import json
import requests   
        
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
