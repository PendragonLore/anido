# -*- coding: utf-8 -*-

import urllib.parse

from . import utils


class StreamPageParser:
    __slots__ = ("url", "session")

    def __init__(self, url, session):
        self.url = url
        self.session = session

    def parse(self):
        tree = utils.request_tree(self.session, self.url)

        for node in tree.xpath("//div/table[2]/tbody/tr")[1:]:
            yield self.normalize_result_url(node.find("./td[2]/a").get("href"))

    def normalize_result_url(self, url):
        url = url.lstrip("/")

        if not url.startswith("http") and not url.startswith("ds.php"):
            url = "https://" + url

        parsed_url = urllib.parse.urlparse(url)
        has_filename = "file" in urllib.parse.parse_qs(parsed_url.query)

        # relative url to the site
        if not parsed_url.netloc:
            url = "https://ww1.animeforce.org/" + url

        return url, has_filename

    def get_episode_direct_url(self, url):
        tree = utils.request_tree(self.session, url)

        return tree.find(".//div[@id='wtf']/a").get("href")
