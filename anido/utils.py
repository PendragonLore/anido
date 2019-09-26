# -*- coding: utf-8 -*-

import os
import pathlib
import shutil
import uuid

import requests
from lxml import etree


def request_tree(session: requests.Session, url: str) -> etree._Element:
    with session.get(url) as response:
        return etree.fromstring(response.text, etree.HTMLParser(encoding="utf-8"))


class AtomicFile:
    __slots__ = ("file", "temp")

    def __init__(self, file: pathlib.Path, *args, **kwargs):
        self.file = file
        self.temp = open(f"{file.resolve()}-{uuid.uuid4().hex}.temp", *args, **kwargs)

    def __enter__(self):
        return self.temp

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.name != "nt":
            self.temp.flush()
            os.fsync(self.temp.fileno())
            self.temp.close()
            os.rename(self.temp.name, str(self.file.resolve()))
        else:
            # win is gay
            self.temp.close()
            shutil.copy2(self.temp.name, str(self.file.resolve()))
            os.remove(self.temp.name)
