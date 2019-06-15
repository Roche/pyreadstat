"""
Test if the version in pyreadstat __init__ matches the version in setup.py
"""

import os
import sys
import re

script_folder = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
sys.path.insert(0, script_folder)
import pyreadstat

pyreadstat_version = pyreadstat.__version__

with open(os.path.join(script_folder, "setup.py")) as h:
    content = h.read()

raw = re.findall("version=\'.*?\'", content)
setup_version = raw[0].replace("version=", "")
setup_version = setup_version.replace("'", "")
print("testing if versions match")
assert(pyreadstat_version == setup_version)
print("versions match!")



