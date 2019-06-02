#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import json
from helpers import unique


def fetch_links():
    import helpers
    text = helpers.get_contents("C:\\src\\NMT\\wte\\txt\\links.txt")
    lines = text.split("\n")
    result = []
    for line in lines:
        if line.find("wiki/Vorlage:") != -1:
            st = line.find("wiki/Vorlage:")
            st += len("wiki/Vorlage:")
            result.append(line[st:])
    
    result = unique(result)
    result.sort()
    print(result)
            
#fetch_links()
#exit(3)


def clean_name(s):
    op = s.find("{{")
    if op!= -1:
        cl1 = s.find("}}", op)
        cl2 = s.find("|", op)
        
        # with second arg
        if cl2 != -1:
            cl22 = s.find("|", cl2+1)
            if cl22 != -1:
                cl2 = cl22
        
        if cl1 != -1 and cl2 != -1:
            if cl1 < cl2:
                cl = cl1
            else:
                cl = cl2
        elif cl1 != -1:
            cl = cl1
        elif cl2 != -1:
            cl = cl2
        else:
            cl = -1
            
        if cl != -1:
            value = s[op+2:cl]
            if value.startswith("s|"):
                value = value.replace("s|", "")
            #if value.startswith("wortart|"):
            #    value = value.replace("wortart|", "")
            return value
    return s
    
    
def doit(lang, word, exclude, filename, title1, title2):
    word = word.lower()
    with open(os.path.join("sections-templates", lang, filename ), "r", encoding="utf-8") as f:    
        d = json.load(f)
        
        result = [] # sections
        keys = [] # raw sections
        
        for v in d.keys():
            cleaned = clean_name(v).lower()
            
            if cleaned.find(word) != -1:
                for excl in exclude:
                    if cleaned.find(excl) != -1:
                        break
                else:
                    result.append(cleaned)
                    keys.append(v)
        
        result = unique(result)
        result.sort()
        
        print(title1)
        print("-", result)

        # templates
        tpls = []
        for k in keys:
            tpls += d[k]
        tpls = unique(tpls)
        tpls.sort()
                
        print("")
        print(title2)
        print("  -", tpls)
        
        # filter
        # for t in tpls:
            # if t.find("|deutsch") != -1:
                # t = t.replace("|deutsch", '')
                # print(t)


lang = "ru"
word = "гл ru "
word = "intro"
exclude = ["<!--"]

print("WORD:", lang+",", word)
print("")
doit(lang, word, exclude, "templates.json", "TEMPLATES:", "  SECTIONS:")
print("")
doit(lang, word, exclude, "sections.json", "SECTIONS:", "  TEMPLATES:")

