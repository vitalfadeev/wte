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

#test_one("en", "cat")
#test_one("en", "do")
#test_one("en", "doing")
#test_one("en", "done")
#test_one("en", "did")
#test_dump("en")
#test_one("fr", "dun")
#test_one("fr", "faire")
#test_one("fr", "cat")
#test_one("fr", "chatte")
#test_dump("fr")
#test_one("de", "Katze")
#test_one("de", "machen")
#test_one("de", "mache")
#test_one("de", "tun")
#test_one("de", "Torben")
#test_dump("de")
#test_one("it", "gatto")
#test_one("it", "gatti")
#test_one("it", "gatta")
#test_one("it", "fare")
#test_one("it", "faccio")
#test_one("it", "farò")
#test_one("it", "fatto")
#test_one("it", "gatte")
#test_one("it", "fare")
#test_one("it", "fatto")
#test_dump("it")
#test_one("pt", "gato")
#test_one("pt", "professor")
#test_one("pt", "professora")
#test_one("pt", "fazer")
#test_one("pt", "decolar")
#test_one("pt", "novo")
#test_one("pt", "fazia")
#test_one("pt", "fazemos")
#test_one("pt", "fará")
test_dump("pt")
#test_one("es", "gato")
#test_one("es", "gata")
#test_one("es", "gatas")
#test_one("es", "gatos")
#test_one("es", "do")
#test_one("es", "dos")
#test_one("es", "haciendo")
#test_one("es", "hacendar")
#test_one("es", "afortunado")
#test_one("es", "car")
#test_one("es", "uña")
#test_one("es", "ónfalos")
#test_one("es", "abeja")
#test_one("es", "ebanista")
#test_one("es", "Oslo")
#test_one("es", "tildarse")
#test_one("es", "chozar")
#test_one("es", "azoto")
#test_dump("es")
#test_read()
#test_wikidict("fr")
