#!/bin/env python3

import requests
import bz2
from wiki_text_tokenizer import get_contents
from en import get_words

#treemap = wt.parse_dump(local_file, limit=1000, is_save_txt=True, is_save_json=True)

def test_cat():
    text = get_contents("test/cat.txt")
    for i, w in enumerate(get_words("en", "cat", text)):
        print(w.LabelName, w.Type, w.LabelType, w.Explaination)
        w.save_to_json("out/cat-" + str(i+1) + ".json")

# parse
"""
with requests.get('https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2', stream=True) as req:
    with bz2.open(req.raw, "r") as fin:
        for (label, text) in wikitionary_xml_reader(fin):
            for (i, w) in enumerate(get_words("en", label, text)):
                print(w.LabelName, w.Type, w.LabelType, w.Explaination)
"""

test_cat()