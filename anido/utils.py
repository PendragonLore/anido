# -*- coding: utf-8 -*-

import os
import shutil
import uuid

from lxml import etree


def request_tree(session, url):
    with session.get(url) as response:
        return etree.fromstring(response.text, etree.HTMLParser(encoding="utf-8"))


class AtomicFile:
    def __init__(self, file):
        self.file = file
        self.temp = open(f"{file.resolve()}-{uuid.uuid4().hex}.temp", "wb+")

    def __enter__(self):
        return self.temp

    def __exit__(self, exc_type, exc_val, exc_tb):
        if os.name != "nt":
            self.temp.flush()
            os.fsync(self.temp.fileno())
            self.temp.close()
            os.rename(self.temp.name, self.file.resolve())
        else:
            # win is gay
            self.temp.close()
            shutil.copy2(self.temp.name, self.file.resolve())
            os.remove(self.temp.name)
