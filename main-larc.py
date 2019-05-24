#!/usr/bin/python3
# -*- coding: utf-8 -*-

from lark import Lark


json_parser = Lark(r"""
    article: header

    section  : _NL "=" STRING "=" _NL link
    content  : template
    header   : _NL "=" TITLE "=" _NL
    template : "{{" NAME "}}"
    link     : "[" NAME "]"
    TITLE: /[^=]+/+
    NAME: /[A-Za-z0-9]+/+
    
    %import common.ESCAPED_STRING   -> STRING
    %import common.WS
    %import common.NEWLINE -> _NL
    
    """, start='article')


text = """
=Header=
[abc]
"""
parsed = json_parser.parse(text)
print(parsed)

