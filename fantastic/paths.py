import os
import platform

if "MacBook-Pro-de-Benjamin" in platform.node():
    BASE_DIR = "/Users/benjaminpoux/Documents/dev"
elif "charlottes-mbp" in platform.node() or "Charlottes-MacBook-Pro" in platform.node() \
    or "Charlottes-MBP" in platform.node():
    BASE_DIR = "/Users/charlotte/Desktop/Info/CartableFantastique"
else:
    BASE_DIR = "/Users/alicharara/Documents"


XML_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1-data", "data", "exs")
JSON_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1-data", "data", "json_exs")
UNTAGGED_EXCEL = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1-data", "data", "ClassementExercices.xlsx")
TAGGED_EXCEL = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1-data", "data", "cleaned_excel.xlsx")
OUTPUT_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1-data", "output")
FANTASTIC_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1", "fantastic")
TEMPLATE_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1", "jinja", "html")
TAG_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1", "tagging")
DATA_DIR = os.path.join(BASE_DIR, "cartable-fantastique-fall-2021-p1-data")
CORRECTION_DIR = os.path.join(FANTASTIC_DIR, "correction")
