# -*- coding: utf-8 -*-

import sys

import click
import requests

from anido import SearchResultParser, StreamDownloader, StreamPageParser

session = requests.Session()


@click.group()
def main():
    pass


@main.command(name="search")
@click.argument("query", nargs=-1)
def cmd_search(query):
    extract_search_results(" ".join(query))


@main.command(name="download")
@click.option("--all", "_all", help="Whether to download all episodes available.",
              required=False, default=False, is_flag=True)
@click.argument("query", nargs=-1)
def cmd_download(query, _all):
    results = extract_search_results("".join(query))

    if len(results) == 1:
        click.confirm(f"Going to download {results[0].text}, is that ok?", abort=True)
        to_download = results[0]
    else:
        prompt = click.prompt("Please pick a series by index", type=int)

        try:
            to_download = results[prompt - 1]
        except IndexError:
            return click.echo("That index isn't present in the list.")

    extract_direct_download_links(to_download.url, download_all=_all)


def extract_search_results(query):
    results = SearchResultParser("https://ww1.animeforce.org", {"s": query}, session).parse()

    if not results:
        click.echo("No results found, exiting.")
        sys.exit(0)

    click.echo(f"Found {len(results)} result(s), extracting data...")

    click.echo("-" * 20)
    click.echo()

    for index, result in enumerate(results, 1):
        click.echo(f"{index}. {result.text} ( {result.url} )")

    click.echo()
    click.echo("-" * 20)

    return results


def extract_direct_download_links(url, *, download_all):
    click.echo("\nExtracting direct urls...")

    parser = StreamPageParser(url, session)

    for index, (url, is_downloadable) in enumerate(parser.parse(), 1):
        # vvvvid or something friendly probably
        if not is_downloadable:
            # TODO: actually scrape the episode number (since it could also be an OVA, special episode, etc...)
            click.echo(f"Episode {index: <3} is not downloadable -> {url}")
            continue

        actual_url = parser.get_episode_direct_url(url)

        # TODO: see above lol
        click.echo(f"Episode {index: <3} -> {actual_url}")

        downloader = StreamDownloader(session, actual_url)

        if download_all:
            downloader.download()
            continue

        if click.confirm(
                "Would you like to download this episode? (pass the --all option when starting to download all)"
        ):
            downloader.download()


if __name__ == "__main__":
    try:
        main()
    finally:
        session.close()
