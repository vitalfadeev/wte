#!/bin/env python3

import wte


def test_one(label, lang):
    wte.one_file(label, lang)

def test_wiktionary(lang):
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


def test_merger():
    from merger import mainfunc as merge
    merge()


test_wiktionary("fr")
test_wiktionary("en")
test_wiktionary("de")
test_wiktionary("it")
test_wiktionary("pt")
test_wiktionary("es")
test_wiktionary("ru")

test_wikidict("fr")
test_wikidict("en")
test_wikidict("de")
test_wikidict("it")
test_wikidict("pt")
test_wikidict("es")
test_wikidict("ru")

test_merger()
