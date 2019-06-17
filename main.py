#!/bin/env python3


def test_one(label, lang):
    from wte import one_file as wiktionary_parser_one
    wiktionary_parser_one(label, lang)


def test_wiktionary(lang):
    from wte import mainfunc as wiktionary_parser
    wiktionary_parser(lang=lang, limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False)


def test_wikidict(lang):
    from wikidict_convertor import run as wikidict_parser
    wikidict_parser("./wikidict-out.json", lang)


def test_merger():
    from merger import mainfunc as merge
    merge()


#test_wikidict("fr")
#test_wiktionary("fr")
#test_merger()
#exit(9)

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
