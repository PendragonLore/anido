# -*- coding: utf-8 -*-

import contextlib
import sys

import httpx
import yarl
from lxml import etree

client = httpx.Client()


def request_and_return_tree(url):
    with contextlib.closing(client.get(str(url))) as response:
        if response.status_code != 200:
            raise RuntimeError(f"Request responded with {response.status_code} ({response.reason_phrase})")

        return etree.fromstring(response.text, etree.HTMLParser())


def extract_search_results(query):
    url = yarl.URL.build(
        scheme="https",
        host="ww1.animeforce.org",
        query={"s": query}
    )

    tree = request_and_return_tree(url)

    results = tree.xpath("//div[@class='article-excerpt']/h2/a")

    if not results:
        print("No results found, exiting.")
        exit(0)

    print(f"Found {len(results)} result(s), extracting data...")

    results = [(node.get("href"), node.text) for node in results]

    print()
    print("-" * 20)
    print()

    for index, (url, title) in enumerate(results, 1):
        print(f"{index}. {title} ( {url} )")

    print()
    print("-" * 20)

    inp = input("Which would you like to view? (input 0 to exit) >> ")

    if inp == "0":
        exit(0)

    try:
        return results[int(inp) - 1][0]
    except IndexError:
        print("Index not present in list.")
    except ValueError:
        print("Must pass an integer.")


def extract_direct_download_links(url):
    print()

    print("Extracting direct urls...")

    tree = request_and_return_tree(url)

    for index, node in enumerate(tree.xpath("//div/table[2]/tbody/tr")[1:], 1):
        url = node.find("./td[2]/a").get("href").lstrip("/")

        # manipulation due to how urls are structured here
        if not url.startswith("http") and not url.startswith("ds.php"):
            url = "https://" + url

        yarl_url = yarl.URL(url)
        has_filename = "file" in yarl_url.query

        # relative url to the site
        if not yarl_url.is_absolute():
            url = "https://ww1.animeforce.org/" + url

        # vvvvid or something friendly probably
        if has_filename is None:
            print(f"Episode {index: <3} -> {url}")
        else:
            another_tree = request_and_return_tree(url)
            actual = another_tree.xpath("//div[@id='wtf']/a")[0]
            print(f"Episode {index: <3} -> {actual.get('href')}")


def main():
    if len(sys.argv) == 1:
        print("No arguments provided.\n"
              "This *would* return the latest episodes out, but that isn't supported... yet.\n"
              "So, goodbye.")
        exit(2)

    picked = extract_search_results(" ".join(sys.argv[1:]))
    extract_direct_download_links(picked)


if __name__ == "__main__":
    main()
