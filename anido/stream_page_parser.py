# -*- coding: utf-8 -*-

import typing
import urllib.parse

import requests

from . import utils


class StreamPageParser:
    __slots__ = ("url", "session")

    def __init__(self, url: str, session: requests.Session):
        self.url: str = url
        self.session: requests.Session = session

    def parse(self) -> typing.Iterator[str]:
        tree = utils.request_tree(self.session, self.url)

        for node in tree.xpath("//div/table[2]/tbody/tr")[1:]:
            yield self.normalize_result_url(node.find("./td[2]/a").get("href"))

    @staticmethod
    def normalize_result_url(url: str) -> typing.Tuple[str, bool]:
        url = url.lstrip("/")

        if not url.startswith("http") and not url.startswith("ds.php"):
            url = "https://" + url

        parsed_url = urllib.parse.urlparse(url)
        has_filename = "file" in urllib.parse.parse_qs(parsed_url.query)

        # relative url to the site
        if not parsed_url.netloc:
            url = "https://ww1.animeforce.org/" + url

        return url, has_filename

    def get_episode_direct_url(self, url: str) -> typing.Optional[str]:
        tree = utils.request_tree(self.session, url)
        a = tree.find(".//div[@id='wtf']/a")

        if a is None:
            return None

        return a.get("href")
