#!/bin/env python3

import wte


def test_cat():
    wte.one_file("en", "cat")

def test_one(label, lang="en"):
    wte.one_file(label, lang)

def test_dump(lang="en"):
    wte.mainfunc(lang=lang, limit=0, is_save_txt=False, is_save_json=False)

#test_one("en", "cat")
test_dump("en")
