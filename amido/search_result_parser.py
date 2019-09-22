# -*- coding: utf-8 -*-

import urllib.parse
from dataclasses import dataclass

import requests

from . import utils


@dataclass
class ParseResult:
    url: str
    text: str


class SearchResultParser:
    def __init__(self, url: str, query: dict, session: requests.Session):
        self.url = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
        self.session = session
        self.results = None

    def parse(self):
        tree = utils.request_tree(self.session, self.url)
        self.results = ret = tree.xpath("//div[@class='article-excerpt']/h2/a")

        return [ParseResult(node.get("href"), node.text) for node in ret]

    @property
    def has_results(self):
        return bool(self.results)
