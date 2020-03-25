#
# cco.processor.importer
#

import csv
from os.path import join


def import_csv(import_dir, fn):
    path = join(import_dir, fn)
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

