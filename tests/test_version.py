"""
Test if the version in pyreadstat __init__ matches the version in setup.py
"""

import os
import sys
import re

script_folder = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.insert(0, script_folder)
sys.path.insert(1,os.path.join(script_folder, "docs"))

import pyreadstat
import conf

pyreadstat_version = pyreadstat.__version__

with open(os.path.join(script_folder, "setup.py")) as h:
    content = h.read()

raw = re.findall("version=\'.*?\'", content)
setup_version = raw[0].replace("version=", "")
setup_version = setup_version.replace("'", "")

with open(os.path.join(script_folder, "CITATION.cff")) as h:
    content = h.readlines()
raw = [x for x in content if x.startswith("version")]
cff_version = raw[0].replace("version:", "").strip()

print("testing if module and setup versions match")
assert(pyreadstat_version == setup_version)
print("testing if documentation and setup versions match")
assert(conf.release == setup_version)
print("testing if cff and setup versions match")
assert(cff_version == setup_version)
print("all versions match!")



