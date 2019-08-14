#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import bz2
import itertools
import decimal

try:
    import ijson.backends.yajl2_cffi as ijson
except:
    import ijson
import json


def clean_surrogates(s):
    if isinstance(s, str):
        return s.encode('utf-16', 'surrogatepass').decode('utf-16')
    else:
        return s


class DataEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)

        # default
        return json.JSONEncoder.default(self, obj)


def split(infile, items_in_chunk):
    counter = itertools.count(1)

    with bz2.open(infile, "rb") as fin:
        for i, data in enumerate(ijson.items(fin, "item"), start=1):
            outfile = infile + "-{}.bz2".format(counter)
            fout = bz2.open(outfile, "wt")

            fout.write("[")

            if i > 1:
                fout.write(",")

            if i % 10 == 0:
                print(i)

            s = json.dumps(data, cls=DataEncoder, sort_keys=False, ensure_ascii=False, indent=None)
            s = clean_surrogates(s)
            fout.write(s)

            if i > items_in_chunk:
                break

            fout.write("]")


def decode_test(local_file):
    with bz2.open(local_file, "rb") as fin:
        reader = enumerate(ijson.items(fin, "item"))
        for i, data in reader:
            print (i, data['id'])


if __name__ == "__main__":
    infile  = os.path.join("cached", "wikidata-20190701-all.json.bz2")
    split(infile, 20)

