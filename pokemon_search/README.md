## Pokemon Search

This is a simple flask app to search Pokemon cards. All Pokemon cards are pulled from the Pokemon TCG Developers API then indexed into a local instance of Elasticsearch. A basic searchbar UI serves as the frontend. 

In order to run this app you need to have Elasticsearch installed and running locally. Gathering the data and indexing is handled in a Luigi pipeline. It is probably best to install requirements in a virtual environmant. So after you cd into the directory launch your virual environment and install requirements. 

```
source venv/bin/activate

pip install -r requirements.txt
```

To run the Luigi pipeline run the command:

```
PYTHONPATH=. luigi --module index_pokemon indexDocuments --local-scheduler
```

Then to get the app up and running:
```
python pokemon.py
```

You should see something like:

```
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger pin code: 375-179-629
```
 
 You can then open up a tab on your browser at http://localhost:5000/
 
 
