#!/bin/env python3

import wte


def test_one(label, lang):
    wte.one_file(label, lang)

def test_dump(lang):
    wte.mainfunc(lang=lang, limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False)

def test_read():
    import sql
    rows = sql.SQLReadDB(sql.DBWikictionary, {"id": 1})
    print(rows)

    rows = sql.SQLReadDB(sql.DBWikictionary, {"LabelName": "free"})
    print(rows)

    rows = sql.SQLReadDB(sql.DBWikiData, {"LabelName": "bonheur"})
    print(rows)

def test_wikidict(lang):
    import wikidict_convertor
    wikidict_convertor.run("./wikidict-out.json", lang)

#test_one("fr", "do")
#test_one("fr", "cat")
#test_one("de", "Frieden")
#test_one("de", "machen")
#test_one("de", "tun")
test_dump("fr")
#test_read()
#test_wikidict("fr")
