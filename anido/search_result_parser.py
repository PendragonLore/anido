# -*- coding: utf-8 -*-

import typing
import urllib.parse

import requests
from lxml.etree import _Element as EtreeElement

from . import utils


class SearchResultParser:
    __slots__ = ("url", "session", "results")

    def __init__(self, url: str, query: dict, session: requests.Session):
        self.url: str = f"{url}?{urllib.parse.urlencode(query, doseq=True)}"
        self.session: requests.Session = session
        self.results: typing.Optional[typing.List[EtreeElement]] = None

    def parse(self) -> typing.List[typing.Tuple[str, str]]:
        tree = utils.request_tree(self.session, self.url)
        self.results = ret = tree.xpath("//div[contains(@class, 'anime-card')]/div")

        return [(node.find("./a").get("href"), node.find("./div/p/a/span").text.strip()) for node in ret]

    @property
    def has_results(self) -> bool:
        return bool(self.results)
