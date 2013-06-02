import csv
import doctest
import os
import dateutil.parser

DOCTEST_OPTION_FLAGS = (doctest.NORMALIZE_WHITESPACE |
                        doctest.ELLIPSIS |
                        doctest.REPORT_ONLY_FIRST_FAILURE
                        |doctest.REPORT_NDIFF
                        )


CONVERT = dict(str=lambda i: i.decode('utf8'),
               text=lambda i: i.decode('utf8'),
               int=lambda i: int(i),
               integer=lambda i: int(i),
               float=lambda i: float(i),
               real=lambda i: float(i),
               bool=lambda i: bool(i.upper()[0] in ('T', 'Y', '1')),
               array=lambda i: [j.strip() for j in i.split(',')],
               date=lambda i: dateutil.parser.parse(i).date(),
               time=lambda i: dateutil.parser.parse(i).time(),
               datetime=lambda i: dateutil.parser.parse(i),
               null=lambda i: None)


def readcsv(fname):
    with open(fname) as f:
        data = []
        fields = []
        first = True
        for r in csv.DictReader(f):
            item = {}
            for k, v in r.items():
                if ',' in k:
                    name, type = k.split(',')
                else:
                    name = k
                    type = 'text'
                v = CONVERT[type](v)
                item[name] = v
                if first:
                    fields.append((name, type))
            data.append(item)
            first = False
    return fields, data
