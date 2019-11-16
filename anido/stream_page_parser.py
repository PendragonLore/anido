# -*- coding: utf-8 -*-

import urllib.parse
from typing import Iterator, Optional, Tuple

import requests

from . import utils


class StreamPageParser:
    __slots__ = ("url", "session")

    def __init__(self, url: str, session: requests.Session):
        self.url: str = url
        self.session: requests.Session = session

    def parse(self, episode_range: Optional[range] = None) -> Iterator[Tuple[str, str, bool]]:
        tree = utils.request_tree(self.session, self.url)

        if episode_range is None:
            sli = slice(1, None)
        else:
            # necessary because we need to skip the first element
            # if the range is 0
            start = episode_range.start or (episode_range.start + 1)
            sli = slice(start, episode_range.stop + 1, episode_range.step)

        for node in tree.xpath("//div/table[2]/tbody/tr")[sli]:
            yield (
                node.find("./td[1]/strong").text.strip(),
                *self.normalize_result_url(node.find("./td[2]/a").get("href"))
            )

    @staticmethod
    def normalize_result_url(url: str) -> Tuple[str, bool]:
        url = url.lstrip("/")

        if not url.startswith("http") and not url.startswith("ds.php"):
            url = "https://" + url

        parsed_url = urllib.parse.urlparse(url)
        has_filename = "file" in urllib.parse.parse_qs(parsed_url.query)

        # relative url to the site
        if not parsed_url.netloc:
            url = "https://ww1.animeforce.org/" + url

        return url, has_filename

    def get_episode_direct_url(self, url: str) -> Optional[str]:
        tree = utils.request_tree(self.session, url)
        hyperlink = tree.find(".//div[@id='wtf']/a")

        if hyperlink is None:
            return None

        return hyperlink.get("href")
