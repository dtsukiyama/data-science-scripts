import requests
import yaml

cfg = yaml.load(open('looker_api.yaml', 'r'))['looker']

class LookerApi(object):

    def __init__(self, token, secret, host):
        self.token = token
        self.secret = secret
        self.host = host
        self.session = requests.Session()
        self.auth()

    def auth(self):
        url = '{}{}'.format(self.host,'login')
        params = {'client_id':self.token,
                  'client_secret':self.secret}
        r = self.session.post(url,params=params)
        access_token = r.json().get('access_token')
        print access_token
        self.session.headers.update({'Authorization': 'token {}'.format(access_token)})

    def get_look_info(self,look_id):
        url = '{}{}/{}'.format(self.host,'looks',look_id)
        print url
        params = {}
        r = self.session.get(url,params=params)
        if r.status_code == requests.codes.ok:
            return r.json()

    def get_look(self,look_id):
        url = '{}{}/{}/run/json'.format(self.host,'looks',look_id)
        print url
        params = {}
        r = self.session.get(url,params=params)
        print r
        if r.status_code == requests.codes.ok:
            return r.json()

    def get_all_looks(self):
        url = '{}{}'.format(self.host,'looks')
        print url
        params = {}
        r = self.session.get(url,params=params)
        print r
        if r.status_code == requests.codes.ok:
            return r.json()     
        
    def get_models(self):
        url = '{}{}'.format(self.host,'lookml_models')
        print url
        params = {}
        r = self.session.get(url,params=params)
        print r
        if r.status_code == requests.codes.ok:
            return r.json()      

    def get_roles(self):
        url = '{}{}'.format(self.host,'roles')
        print url
        params = {}
        r = self.session.get(url,params=params)
        print r
        if r.status_code == requests.codes.ok:
            return r.json()
        
    def get_users(self):
        url = '{}{}'.format(self.host,'users')
        print url
        params = {}
        r = self.session.get(url,params=params)
        print r
        if r.status_code == requests.codes.ok:
            return r.json()
            
# example usage: getting basic look, user, and role data
looker = LookerApi(host=cfg['host'],token=cfg['token'],secret = cfg['secret'])
looks = looker.get_all_looks()
