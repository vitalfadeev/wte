#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import wte


DBWikictionary = sqlite3.connect("Wikictionary.db")


def SQLInitDB( conn ):
    sql = """
    CREATE TABLE IF NOT EXISTS wikictionary (
        id BIGINT PRIMARY KEY AUTOINCREMENT,
        LabelName       text,
        LabelType       text,
        LanguageCode    text,
        Type            text,
        ExplainationRaw             text,
        ExplainationTxt             text,
        ExplainationExamplesRaw     text,
        ExplainationExamplesTxt     text,
        IsMale          integer,
        IsFeminine      integer,
        IsSingle        integer,
        IsPlural        integer,
        SingleVariant   text,
        PluralVariant   text,
        IsVerbPast      integer,
        IsVerbPresent   integer,
        IsVerbFutur     integer,
        Conjugation     text,
        Synonymy	    text,
        Antonymy	    text,
        Hypernymy	    text,
        Hyponymy	    text,
        Meronymy	    text,
        Holonymy	    text,
        Troponymy	    text,
        Otherwise_related       text,
        AlternativeFormsOther   text,
        RelatedTerms            text,
        Coordinate_term         text,
        Translation_EN  text,
        Translation_FR  text,
        Translation_DE  text,
        Translation_IT  text,
        Translation_ES  text,
        Translation_RU  text,
        Translation_PT  text
    )
    """
    
    c = DBWikictionary.cursor()
    c.execute(sql)
    
    # indexes
    

def SQLWriteDB( DB, worddict ):
    # prepare    
    for label, words in worddict.items():
        for word in words:
            fields = []
            values = []
            placeholders = []
            
            for name in word.get_fields():
                value = getattr(word, name)
                
                if value:                
                    if isinstance(value, list):
                        value = json.dumps(value, cls=wte.WordsEncoder, sort_keys=False, indent=4, ensure_ascii=False)
                    
                    fields.append(name)
                    values.append(value)
                    placeholders.append("?")

            # insert
            c = DB.cursor()
            sql = """
            INSERT INTO wikictionary 
                ({})
                VALUES
                ({})
            """.format(",".join(fields), ",".join(placeholders))
            #print(sql)
            c.execute(sql, values)
            
        DB.commit()

    
def SQLReadDB( DB, DictSearch ):
    # DictSearch = {"id":1, "LabelName":"cat", "Type":"noun"}

    fields = []
    placeholders = []
    values = []
    expressions = []

    for k,v in DictSearch.items():
        fields.append(k)
        values.append(v)
        placeholders.append('?')
        expressions.append( k + "= ?" )

    c = DB.cursor()

    sql = """
    SELECT * 
      FROM wikictionary 
     WHERE 
        {}
    """.format( ",".join(expressions) )

    result = c.execute(sql, values)

    return result
    

"""
DBWikiData = sqlite3.connect("WikiData.db")

PrimaryIndex  (long integer start at 10^7) * 3 
LabelName
CodeInWiki (like Q300918)
LanguageCode (EN,FR,…)
Description
AlsoKnownAs1
AlsoKnownAs2
AlsoKnownAs3
AlsoKnownAs4
AlsoKnownAs5

SelfUrl (https://www.wikidata.org/wiki/Q300918)
Wikipedia URL (https://en.wikipedia.org/wiki/Cat_(Unix))
DescriptionUrl ( Great Russian Encyclopedia Online ID, Encyclopædia Britannica Online ID, Encyclopædia Universalis ID, described at URL / official link / etc... )

[ ] Instance-of
[ ] Subclass-of
[ ] Part-of

[ ] Translation-EN  
[ ] Translation-FR 
[ ] Translation-DE 
[ ] Translation-IT 
[ ] Translation-ES 
[ ] Translation-RU 
[ ] Translation-PT 


# index
PrimaryIndex 
LabelName
CodeInWiki (like Q300918)
LanguageCode (EN,FR,…)
AlsoKnownAs1
AlsoKnownAs2
AlsoKnownAs3
AlsoKnownAs4
AlsoKnownAs5

# arrays are stored as a json 


DBWikictionary = sqlite3.connect("Wikictionary.db")

PrimaryIndex  (long integer start at 10^7) * 5 
LabelName
LabelType 
LanguageCode (EN,FR,DE,IT,ES,RU,PT)
Type 
ExplainationRaw
ExplainationTxt

[ ] ExplainationExamplesRaw
[ ] ExplainationExamplesTxt
IsMale
IsFeminine
IsSingle
IsPlural
SingleVariant
PluralVariant

IsVerbPast
IsVerbPresent
IsVerbFutur
[ ] Conjugation

[ ] Translation-EN  
[ ] Translation-FR 
[ ] Translation-DE 
[ ] Translation-IT 
[ ] Translation-ES 
[ ] Translation-RU 
[ ] Translation-PT 

[ ] Synonymy	
[ ] Antonymy	
[ ] Hypernymy	
[ ] Hyponymy	
[ ] Meronymy	
[ ] Holonymy	
[ ] Troponymy	
[ ] Otherwise related 
[ ] AlternativeFormsOther 
[ ] RelatedTerms 
[ ] Coordinate term

# indexes
LabelName
LabelType 
LanguageCode (EN,FR,DE,IT,ES,RU,PT)

# ALL arrays are stored as a json string 

def SQLWriteDB( DB, Dict )

# Wikidata check this key CodeInWiki
# Wikictionary check both LabelName + LabelType (Select where LabelName="..." and LabelType="...")

def SQLReadDB( DB, DictSearch )
    # return json Dict 
    # Example : { 'LabelName' : 'cat' , 'LabelType' : 'felidae' }


"""


SQLInitDB( DBWikictionary )
