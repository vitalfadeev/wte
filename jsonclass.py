#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import inspect
from blist import sorteddict


class JSONClass:
    def save_to_json(self, filename):
        save_to_json(self, filename)


    def as_json(self):
        return json.dumps(self, cls=JSONEncoder, sort_keys=False, indent=4, ensure_ascii=False)
        

class JSONEncoder(json.JSONEncoder):
    """
    This class using in JSON encoder.
    Take object with Word objects and return dict.
    """
    def default(self, obj):
        if callable(obj):
            return None # skip
            
        elif inspect.ismethod(obj):
            return None # skip

        elif isinstance(obj, object) and hasattr(obj, "get_fields"):
            # Word
            return { f:getattr(obj, f) for f in obj.get_fields() }

        elif isinstance(obj, sorteddict):
            # sorteddict
            return dict(obj.items())

        # default
        return json.JSONEncoder.default(self, obj)
