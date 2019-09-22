# -*- coding: utf-8 -*-

from lxml import etree


def request_tree(session, url):
    with session.get(url) as response:
        return etree.fromstring(response.text, etree.HTMLParser(encoding="utf-8"))
