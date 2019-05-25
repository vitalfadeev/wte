#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import wte
import wikidict_convertor


DBWikictionary = sqlite3.connect("Wikictionary.db")
DBWikiData = sqlite3.connect("WikiData.db")


def get_new_id(DB):
    c = DB.cursor()
    sql_table = "wikictionary" if DB == DBWikictionary else "wikidata"

    sql = """
    SELECT max(id) as id 
      FROM {}
    """.format(sql_table)

    c.execute(sql)
    rows = c.fetchall()

    if rows and rows[0][0]:
        get_new_id = rows[0][0] + 1

    else:
        get_new_id = 1

    return get_new_id

def SQLInitDB():
    sql = """
    CREATE TABLE IF NOT EXISTS wikictionary (
        id              BIGINT,
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
        MaleVariant     text,
        FemaleVariant   text,
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
        Otherwise               text,
        AlternativeFormsOther   text,
        RelatedTerms            text,
        Coordinate              text,
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


    sql = """
    CREATE TABLE IF NOT EXISTS wikidata (
        id              BIGINT,
        LabelName       text,
        CodeInWiki      text,
        LanguageCode    text,
        Description     text,
        AlsoKnownAs1    text,
        AlsoKnownAs2    text,
        AlsoKnownAs3    text,
        AlsoKnownAs4    text,
        AlsoKnownAs5    text,
        SelfUrl         text,
        WikipediaURL    text,
        DescriptionUrl  text,        
        Instance_of     text,
        Subclass_of     text,
        Part_of         text,
        Translation_EN  text,    
        Translation_FR  text,
        Translation_DE  text,
        Translation_IT  text,
        Translation_ES  text,
        Translation_RU  text,
        Translation_PT  text
    ) 
    """

    c = DBWikiData.cursor()
    c.execute(sql)

    # indexes
    # index
    #PrimaryIndex
    #LabelName
    #CodeInWiki(like
    #Q300918)
    #LanguageCode(EN, FR,…)
    #AlsoKnownAs1
    #AlsoKnownAs2
    #AlsoKnownAs3
    #AlsoKnownAs4
    #AlsoKnownAs5


def SQLWriteDB( DB, worddict ):
    """
    SQLWriteDB( DBWikictionary, {label:[word, word,...]} )
    """
    sql_table = "wikictionary" if DB == DBWikictionary else "wikidata"
    cls_encoder = wikidict_convertor.ItemClassEncoder if DB == DBWikiData else wte.WordsEncoder

    # prepare    
    for label, words in worddict.items():
        for word in words:
            fields = []
            values = []
            placeholders = []

            newid = get_new_id(DB)
            fields.append("id")
            values.append(newid)
            placeholders.append("?")

            for name in word.get_fields():
                value = getattr(word, name)
                
                if value:
                    # list to JSON                    
                    if isinstance(value, list):
                        value = json.dumps(value, cls=cls_encoder, sort_keys=False, indent=4, ensure_ascii=False)
                    elif isinstance(value, dict):
                        value = json.dumps(value, cls=cls_encoder, sort_keys=False, indent=4, ensure_ascii=False)
                    
                    fields.append(name)
                    values.append(value)
                    placeholders.append("?")

            # insert
            c = DB.cursor()
            sql = """
            INSERT INTO {}
                ({})
                VALUES
                ({})
            """.format(
                sql_table, 
                ",".join(fields), 
                ",".join(placeholders)
                )
            c.execute(sql, values)
            
        DB.commit()

    
def SQLReadDB( DB, DictSearch ):
    """
    rows = SQLReadDB( DBWikictionary, {"id":1, "LabelName":"cat", "Type":"noun"} )
    """
    sql_table = "wikictionary" if DB == DBWikictionary else "wikidata"
    
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
      FROM {}
     WHERE 
        {}
    """.format( 
        sql_table,
        ",".join(expressions) 
        )

    c.execute(sql, values)
    rows = c.fetchall()

    result = []

    if DB == DBWikictionary:
        for row in rows:
            import wte
            import json
            word = wte.Word()

            for idx, col in enumerate(c.description):
                cname = col[0]
                cvalue = row[idx]

                if cvalue and  cname in ("Synonymy", "Antonymy",
                                         "Hypernymy", "Hyponymy", "Meronymy", "Holonymy",
                                         "Troponymy", "Otherwise", "AlternativeFormsOther",
                                         "RelatedTerms", "Coordinate", "Translation_EN",
                                         "Translation_FR", "Translation_DE", "Translation_IT",
                                         "Translation_ES", "Translation_RU", "Translation_PT"):
                    cvalue = json.loads(cvalue)

                setattr(word, cname, cvalue)

            result.append(word)

    else:
        for row in rows:
            import wikidict_convertor
            import json
            word = wikidict_convertor.ItemClass()

            for idx, col in enumerate(c.description):
                cname = col[0]
                cvalue = row[idx]

                if cvalue and  cname in ("DescriptionUrl",
                                         "Instance_of", "Subclass_of", "Part_of"):
                    cvalue = json.loads(cvalue)

                setattr(word, cname, cvalue)

            result.append(word)

    return result
    

"""
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


SQLInitDB()
