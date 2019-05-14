import logging
import datetime
import os

from django import template
from django.conf import settings

import ujson as json

register = template.Library()


@register.inclusion_tag("scripts.html", takes_context=True)
def react_js(context):
    path = os.path.join(settings.BASE_DIR, "frontend", "webpack-stats.json")
    with open(path, "r") as of:
        contents = json.loads(of.read())

    status = contents["status"]
    if status == "compiling":
        return []

    chunks = contents["chunks"]
    js_files = []
    for name, chunk in chunks.items():
        for _chunk in chunk:
            name = _chunk["name"]
            if name.split(".")[-1] in ["js", "map"]:
                logging.debug(_chunk)
                js_files.append(_chunk["name"])
    return {"scripts": js_files, "publicPath": contents["publicPath"]}


@register.inclusion_tag("styles.html", takes_context=True)
def react_css(context):
    path = os.path.join(settings.BASE_DIR, "frontend", "webpack-stats.json")
    with open(path, "r") as of:
        contents = json.loads(of.read())

    status = contents["status"]
    if status == "compiling":
        return []

    chunks = contents["chunks"]
    css_files = []
    for name, chunk in chunks.items():
        for _chunk in chunk:
            if name.split(".")[-1] in ["css"]:
                logging.debug(_chunk)
                css_files.append(_chunk["name"])

    return {"styles": css_files, "publicPath": contents["publicPath"]}
