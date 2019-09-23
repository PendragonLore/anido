# -*- coding: utf-8 -*-

import urllib.parse

import requests

from . import utils


class SearchResultParser:
    __slots__ = ("url", "session", "results")

    def __init__(self, url: str, query: dict, session: requests.Session):
        self.url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
        self.session = session
        self.results = None

    def parse(self):
        tree = utils.request_tree(self.session, self.url)
        self.results = ret = tree.xpath("//div[@class='article-excerpt']/h2/a")

        return [(node.get("href"), node.text) for node in ret]

    @property
    def has_results(self):
        return bool(self.results)
