#!/bin/env python3

import wte


def test_one(label, lang):
    wte.one_file(label, lang)

def test_dump(lang):
    wte.mainfunc(lang=lang, limit=0, is_save_txt=False, is_save_json=False)

def test_read():
    import sql
    rows = sql.SQLReadDB(sql.DBWikictionary, {"id": 1})
    print(rows)

    rows = sql.SQLReadDB(sql.DBWikictionary, {"LabelName": "free"})
    print(rows)

#test_one("fr", "do")
#test_one("fr", "cat")
test_dump("en")
#test_read()
