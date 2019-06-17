# wte
Wikitionary word description extractor. Parse the article from the dump of the https://en.wiktionary.org/

Extraction words off 7 languages: en, fr, de, it, es, pt, ru


### Requirements: 
see requirements.txt

      blist
      requests
      ijson
      pywikibot
      wikipedia

install

      pip install -r requirements.txt


#### Using
see main.py

      def test_wiktionary(lang):
          from wte import mainfunc as wiktionary_parser
          wiktionary_parser(lang=lang, limit=0, is_save_txt=False, is_save_json=False, is_save_templates=False)


      def test_wikidict(lang):
          from wikidict_convertor import run as wikidict_parser
          wikidict_parser("./wikidict-out.json", lang)


      def test_merger():
          from merger import mainfunc as merge
          merge()
          
      
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



#### Downloading
Will douwnload dump. Stored into cache folder.

    wt = wte.Wikitionary()
    local_file = wt.download("en", use_cached=True)

Dumps:

    "https://dumps.wikimedia.org/" + lang + "wiktionary/latest/" + lang + "wiktionary-latest-pages-articles.xml.bz2"
    "https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2"


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
         - fixes: 
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

Data saves in SQLite:
* Wikictionary.db
* WikiData.db
* Words.db

Structure:

        # Wiktionary
        LabelName = ""  #
        LabelType = None  #
        LanguageCode = ""  # (EN,FR,…)
        Type = ""  # = noun,verb… see = WORD_TYPES
        TypeLabelName = ""  # chatt for verb of chat
        ExplainationRaw = None  #
        ExplainationTxt = None  #
        ExplainationExamplesRaw = None
        ExplainationExamplesTxt = None
        IsMale = None
        IsFeminine= None  # ""
        IsNeutre= None  # ""
        IsSingle = None
        IsPlural = None
        SingleVariant = None  # ""
        PluralVariant = None  # ""
        MaleVariant = None  # ""
        FemaleVariant = None  # ""
        IsVerbPast = None
        IsVerbPresent = None
        IsVerbFutur = None
        Conjugation = []
        Synonymy = []
        Antonymy = []
        Hypernymy = []
        Hyponymy = []
        Meronymy = []
        Holonymy = []
        Troponymy = []
        Otherwise = []
        AlternativeFormsOther = []
        RelatedTerms = []
        Coordinate = []
        Translation_EN = []
        Translation_FR = []
        Translation_DE = []
        Translation_IT = []
        Translation_ES = []
        Translation_RU = []
        Translation_PT = []

        # Wikidata
        LabelName = None
        LanguageCode = None
        CodeInWiki = None
        Description = None
        AlsoKnownAs = []
        SelfUrl = None
        WikipediaENURL = None
        EncyclopediaBritannicaEN = None
        EncyclopediaUniversalisEN = None
        DescriptionUrl = None
        Instance_of = []
        Subclass_of = []
        Part_of = []
        Translation_EN = []
        Translation_FR = []
        Translation_DE = []
        Translation_IT = []
        Translation_ES = []
        Translation_RU = []
        Translation_PT = []
        
        # Words
        LabelName       = None
        CodeInWiki      = None
        LanguageCode    = None
        Description     = None
        AlsoKnownAs     = None
        SelfUrl         = None
        WikipediaENURL  = None
        EncyclopediaBritannicaEN = None
        EncyclopediaUniversalisEN = None
        Instance_of     = []
        Subclass_of     = []
        Part_of         = []
        Translation_EN  = []
        Translation_FR  = []
        Translation_DE  = []
        Translation_IT  = []
        Translation_ES  = []
        Translation_RU  = []
        Translation_PT  = []
        LabelType       = None
        Type            = None
        Explaination    = None
        ExplainationExamples = []
        IsMale          = None
        IsFeminine      = None
        IsSingle        = None
        IsPlural        = None
        SingleVariant   = None
        PluralVariant   = None
        IsVerbPast      = None
        IsVerbPresent   = None
        IsVerbFutur     = None
        Conjugation     = []
        Synonymy        = []
        Antonymy        = []
        Hypernymy       = []
        Hyponymy	     = []
        Meronymy	     = []
        Holonymy        = []
        Troponymy       = []
        Otherwise       = []
        AlternativeFormsOther = []
        RelatedTerms    = []
        Coordinate      = []
        WikipediaENContent   = None
        BritannicaENContent  = None
        UniversalisENContent = None      
        
Databases created automatically.
Datatables created automatically.
Columns created automatically. 
See dbclass.py


##### Logs
See logs in folder ./logs


##### Language modules
See:

    en.py
    fr.py
    de.py
    it.py
    es.py
    pt.py
    ru.py

    
