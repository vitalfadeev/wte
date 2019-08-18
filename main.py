#!/bin/env python3


def test_one(lang, label):
    from wte import one_file as wiktionary_parser_one
    wiktionary_parser_one(lang, label)


def test_wiktionary(lang):
    from wte import mainfunc as wiktionary_parser
    wiktionary_parser(lang=lang, limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False)


def test_wikidict(lang, from_point=None):
    from wdc import run as wikidict_parser
    wikidict_parser(lang, from_point=from_point)


def test_merger():
    from merger import mainfunc as merge
    merge()


#test_one("es", "amigo")
test_wikidict("en", "Q177")
#test_wiktionary("en")
#test_merger()
exit(9)

test_wiktionary("en")
test_wiktionary("fr")
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
