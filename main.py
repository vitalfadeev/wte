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


test_dump("fr")
test_dump("en")
test_dump("de")
test_dump("it")
test_dump("pt")
test_dump("es")
test_dump("ru")
test_read()
test_wikidict("fr")
test_wikidict("en")
test_wikidict("de")
