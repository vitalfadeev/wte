#!/bin/env python3

# -*- coding: utf-8  -*-
import pywikibot
site = pywikibot.Site("en", "wikipedia")
page = pywikibot.Page(site, u"Douglas Adams")
item = pywikibot.ItemPage.fromPage(page)
dictionary = item.get()
print(dictionary)
print(dictionary.keys())
print(item)

