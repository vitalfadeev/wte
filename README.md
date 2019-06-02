# wte
Wikitionary word description extractor. Parse the article from the dump of the https://en.wiktionary.org/

### Requirements: 
* blist
* requests
* ijson
* pywikibot

    pip install blist
    pip install requests
    pip install ijson
    pip install pywikibot


#### Using
    import wte

#### Downloading
    wt = wte.Wikitionary()
    local_file = wt.download("en", use_cached=True)
    
#### Parsing
    # parse
    wte.mainfunc(lang="en", limit=0, is_save_txt=False, is_save_json=False)

#### Technical description

Script steps:

    prepare:
    in: lang
       - download
       - unpack .bz2
       - parse xml
       - extract page text
    out: text

    preprocess:
    in: text
        - fix '\n'
        - fix UTF-8 BOM
        - check redirect
    out: text

    phase 1: (build tree)
      in: text
        - parse text
        - extract templates {{...}}
        - extract html <...>
        - extract links [[...]]
        - extract character data
        - create object
      out: object tree

    phase 2: (add sections)
      in: object tree
         - buld struct: LANG / Type-of-speech / Explaination
         - fixed: 
           - add absend lang section
           - add headers 
           - extract names from templated headers
           - level of section
         - pack lists
         - pack sections
      out: object tree

    phase 3: (data mining)
      in: object tree
         - scan struct
           - LANG
           - Type-of-speech
           - explainations
         - for each pass:
             - scan sections
             - scan templates
             - scan lists
               - detect singular, plural
               - detect male, female, neutral
               - detect noun, verb, adverb, ...
               - detect past, present, futur
               - detect translations
               - detect synonyms
               - detect antonys, meronyms, heronyms, holonyms, ...
               - detect related
               - detect explainations
               - detect examples
      out: words

    phase 4: (create words)
      in: words
        - ...
      out: words

    postprocess: (save words)
      in: words list
        - save to json
        - save to sql
#
    
    
See also: 
* main.py  

