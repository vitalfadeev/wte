# wte
Wikitionary word description extractor. Parse the article from the dump of the https://en.wiktionary.org/

### Requirements: 
* blist
* requests


    pip install blist
    pip install requests

#### Using
    import wte

#### Downloading
    wt = wte.Wikitionary()
    local_file = wt.download("en", use_cached=True)
    
#### Parsing
    # parse
    wt = wte.Wikitionary()
    treemap = wt.parse_dump(local_file, limit=10, is_save_txt=True, is_save_json=True)
    
#### Saving
    # save to json
    json_filename = os.path.join(".", 'result.json')
    wte.log.info("Saving to the %s", json_filename )
    treemap.save_to_json(json_filename)

    # save to pickle
    pickle_filename = os.path.join(".", "result.pickled")
    wte.log.info("Saving to the %s", pickle_filename )
    treemap.save_to_pickle(pickle_filename)

#### Loading
    # load json
    treemap = wte.TreeMap()
    wte.log.info("Loading from the %s", json_filename )
    treemap.load_from_json(json_filename)
    
    # laod pickle
    treemap = wte.TreeMap()
    wte.log.info("Loading from the %s", pickle_filename )
    treemap.load_from_pickle(pickle_filename)
  
#### Printing
    # show words
    wte.log.info("Printing words: %d words", len(treemap.store))
    for label, words in treemap.store.items():
        print(label.ljust(40), words)
    

See also: 
* main.py  
* importing into the pyCharm [https://github.com/vitalfadeev/wikoo/wiki/7-happy-steps-for-importing-project-into-the-pyCharm]
