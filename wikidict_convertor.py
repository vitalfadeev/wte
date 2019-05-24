#!/usr/bin/python3
# -*- coding: utf-8 -*-

import bz2
import json

import requests
import ijson
import pywikibot
from pywikibot import Claim
from pywikibot.site import DataSite
from blist import sorteddict


class ItemClass:
    def __init__(self):
        self.LabelName = None
        self.LanguageCode = None
        self.Description = None
        self.AlsoKnownAs = None
        self.SelfUrl = None
        self.WikipediaURL = None
        self.DescriptionUrl = None
        self.Instance_of = None
        self.Subclass_of = None
        self.Part_of = None
        self.Translation_EN = None
        self.Translation_FR = None
        self.Translation_DE = None
        self.Translation_IT = None
        self.Translation_ES = None
        self.Translation_RU = None
        self.Translation_PT = None
 
    def save_to_json(self, filename):
        save_to_json(self, filename)

    def as_json(self):
        return json.dumps(self, cls=ItemClassEncoder, sort_keys=False, indent=4, ensure_ascii=False)


class ItemClassEncoder(json.JSONEncoder):
    """
    This class using in JSON encoder.
    Take object with Word objects and return dict.
    """
    def default(self, obj):
        if isinstance(obj, ItemClass):
            # Word
            return {k:v for k,v in obj.__dict__.items() if k[0] != "_"}

        elif isinstance(obj, sorteddict):
            # sorteddict
            return dict(obj.items())

        # default
        return json.JSONEncoder.default(self, obj)


def save_to_json(treemap, filename):
    """
    Save 'treemap' in the file 'filename'. In JSON format. Encoding UTF-8.
    """
    #folder = os.path.dirname(os.path.abspath(filename))
    #create_storage(folder)
    
    with open(filename, "w", encoding="UTF-8") as f:
        json.dump(treemap, f, cls=ItemClassEncoder, sort_keys=False, indent=4, ensure_ascii=False)
 


INSTANCE_OF_ID  = "P31"
PART_OF_ID  = "P361"
SUBCLASS_OF_ID  = "P29"
URL_ID = 'P854'
NAME_ID = 'P1476'


def convert(page, lang):
    words = []
    
    w = ItemClass()
    
    #
    id_       = str(page.id)
    label     = page.labels.get(lang, None)
    aliases   = page.aliases.get(lang, [])
    wikipedia = "https://en.wikipedia.org/wiki/" + page.getSitelink('enwiki')
    
    # description
    desc = page.descriptions.get(lang, None)
       
    # claims    
    claims = page.claims

    #
    instance_of_list = claims.get(INSTANCE_OF_ID, None)

    # description Url 
    # Britanica P1417
    # Universalis P3219
    # https://en.wikipedia.org/wiki/Cat ... https://www.wikidata.org/wiki/Special:SetSiteLink/Q146
    description_url  = {}
    
    BRITANICA_ID = "P1417"    
    if INSTANCE_OF_ID in claims:
        for source in claims.get(BRITANICA_ID, []):
            description_url["UniversalisENURL"] = "https://www.britannica.com/" + source.getTarget()

    UNIVERSAILS_ID = "P3219"    
    if UNIVERSAILS_ID in claims:
        for source in claims.get(UNIVERSAILS_ID, []):
            description_url["BritannicaENURL"] = "https://www.universalis.fr/encyclopedie/" + source.getTarget()

    if wikipedia:
        description_url["WikipediaENURL"] = wikipedia 

    if not description_url:
        description_url = None
       
    # instance of
    if INSTANCE_OF_ID in claims:
        instance_of = []
        for source in claims.get(INSTANCE_OF_ID, []):
            instance_of.append(source.target.id)
    else:
        instance_of = None

    # parts of
    if PART_OF_ID in claims:
        part_of = []
        for source in claims.get(PART_OF_ID, []):
            #url = source.qualifiers.get(URL_ID, None)
            part_of.append(source.target.id)
    else:
        part_of = None
        
    # subclass_of
    subclass_of = None
    if SUBCLASS_OF_ID in claims:
        subclass_of = []
        for source in claims.get(SUBCLASS_OF_ID, []):
            subclass_of.append(source.target.id)
    else:
        subclass_of = None
    
    #
    # https://www.wikidata.org/wiki/Special:EntityData/Q300918.json
    w.Id = id_
    w.LabelName = label
    w.LanguageCode = lang
    w.Description = desc
    w.AlsoKnownAs = aliases
    w.SelfUrl = "https://www.wikidata.org/wiki/" + id_
    w.WikipediaURL = wikipedia
    w.DescriptionUrl = description_url
    w.Instance_of = instance_of
    w.Subclass_of = subclass_of
    w.Part_of = part_of
    w.Translation_EN = page.labels.get("en", None)
    w.Translation_FR = page.labels.get("fr", None)
    w.Translation_DE = page.labels.get("de", None)
    w.Translation_IT = page.labels.get("it", None)
    w.Translation_ES = page.labels.get("es", None)
    w.Translation_RU = page.labels.get("ru", None)
    w.Translation_PT = page.labels.get("pt", None)
    
    words.append(w)
  
    return words
  

class PageGenerator:
    def __init__(self, site):
        self.repo = site

    def get(self, data, force=False):
        self._content = data
        
        # aliases
        self.aliases = {}
        if 'aliases' in self._content:
            for lang in self._content['aliases']:
                self.aliases[lang] = []
                for value in self._content['aliases'][lang]:
                    self.aliases[lang].append(value['value'])

        # labels
        self.labels = {}
        if 'labels' in self._content:
            for lang in self._content['labels']:
                if 'removed' not in self._content['labels'][lang]:  # T56767
                    self.labels[lang] = self._content['labels'][lang]['value']

        # descriptions
        self.descriptions = {}
        if 'descriptions' in self._content:
            for lang in self._content['descriptions']:
                self.descriptions[lang] = self._content[
                    'descriptions'][lang]['value']

        # claims
        self.claims = {}
        if 'claims' in self._content:
            for pid in self._content['claims']:
                self.claims[pid] = []
                for claim in self._content['claims'][pid]:
                    c = Claim.fromJSON(self.repo, claim)
                    c.on_item = self
                    self.claims[pid].append(c)

        return {'aliases': self.aliases,
                'labels': self.labels,
                'descriptions': self.descriptions,
                'claims': self.claims,
                }


class DumpPage(pywikibot.ItemPage):
    def __init__(self, site):
        self.repo = site

    def get(self, data, force=False):
        self._content = data
        
        # aliases
        self.aliases = {}
        if 'aliases' in self._content:
            for lang in self._content['aliases']:
                self.aliases[lang] = []
                for value in self._content['aliases'][lang]:
                    self.aliases[lang].append(value['value'])

        # labels
        self.labels = {}
        if 'labels' in self._content:
            for lang in self._content['labels']:
                if 'removed' not in self._content['labels'][lang]:  # T56767
                    self.labels[lang] = self._content['labels'][lang]['value']

        # descriptions
        self.descriptions = {}
        if 'descriptions' in self._content:
            for lang in self._content['descriptions']:
                self.descriptions[lang] = self._content[
                    'descriptions'][lang]['value']

        # claims
        self.claims = {}
        if 'claims' in self._content:
            for pid in self._content['claims']:
                self.claims[pid] = []
                for claim in self._content['claims'][pid]:
                    c = Claim.fromJSON(self.repo, claim)
                    c.on_item = self
                    self.claims[pid].append(c)

        return {'aliases': self.aliases,
                'labels': self.labels,
                'descriptions': self.descriptions,
                'claims': self.claims,
                }


class DumpDataSite(DataSite):
    def loadcontent(self, identification):
        return self.dump_data
        #return data['entities']

    def data_repository(self):
        return self
        
    def set_dump_data(self, data):
        self.dump_data = data

#class DumpSite(BaseSite):
#    def data_repository(self):
#        return DumpDataSite()


class DumpWrapper:
    def __init__(self):
        self.dumpdata = None
    
    def submit(self, *args, **kvargs):
        return {"entities":self.dumpdata, 'success':1}
        
dump_wrapper = DumpWrapper()

def DumpWrapperFactory(*args, **kvargs):
    return dump_wrapper




def run(outfile, lang="en"):
    site = pywikibot.Site("wikidata", 'wikidata')
    repo = site.data_repository()
    repo._simple_request = DumpWrapperFactory

    print("Result in the:", outfile)

    with requests.get('https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2', stream=True) as req:
      with bz2.open(req.raw, "r") as fin:
        with open(outfile, "w", encoding="utf-8") as fout:
            fout.write("[\n")

            try:
                for i, data in enumerate(ijson.items(fin, "item")):
                    try:
                        print(i, data["id"])
                        data.update({"pageid":1,"ns":0,"title":data["id"],"lastrevid":931882328,"modified":"2019-05-03T10:37:50Z"})
                        dump_wrapper.dumpdata = {data["id"]:data}
                        item = pywikibot.ItemPage(repo, data["id"])
                        item.get()
                        
                        words = convert(item, lang)
                        
                        for w in words:
                            js = w.as_json()
                            
                            if i == 0: 
                                fout.write(js.encode('utf-16','surrogatepass').decode('utf-16'))
                            else:
                                fout.write(",\n")
                                fout.write(js.encode('utf-16','surrogatepass').decode('utf-16'))
                                
                    except pywikibot.exceptions.NoPage:
                        print("no page... [SKIP]")
                        pass
            
            except ijson.common.IncompleteJSONError:
                print("unexpected end of file")
                pass         
                
            fout.write("\n]\n")
        

if __name__ == "__main__":
    run("./wikidict-out.json", "fr")
