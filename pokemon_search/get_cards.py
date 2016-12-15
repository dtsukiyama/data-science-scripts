
import requests
import json

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

with open('data/cards.json', 'w') as outfile:
    json.dump(all_cards, outfile)
