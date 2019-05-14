import re


uuid4hex = re.compile('[0-9a-f]{32}\Z', re.I)

def is_uuid4(string):
    return uuid4hex.match(string)
