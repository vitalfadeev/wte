#!/bin/env python3

# Requirements:
#   pip install blist
#   pip install requests

import os

import wte


if __name__ == "__main__":
    #wikidict.one_file("Czechia")
    #exit(0)
    
    # Download
    wt = wte.Wikitionary()
    local_file = wt.download("en", use_cached=True)
    
    # Parse
    # parse
    treemap = wt.parse_dump(local_file, limit=10, is_save_txt=True, is_save_json=True)
    
    # Save
    # save to json
    json_filename = os.path.join(".", 'result.json')
    treemap.save_to_json(json_filename)

    # save to pickle
    pickle_filename = os.path.join(".", "result.pickled")
    treemap.save_to_pickle(pickle_filename)
    
    # Laod
    # laod json
    treemap = wte.TreeMap()
    treemap.load_from_json(json_filename)
    
    # laod pickle
    treemap = wte.TreeMap()
    treemap.load_from_pickle(pickle_filename)
    
    # Show
    # show words
    for label, words in treemap.store.items():
        print(label.ljust(40), words)
    
    