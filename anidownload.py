# -*- coding: utf-8 -*-

from typing import List, Optional, Tuple

import click
import requests

from anido import SearchResultParser, StreamDownloader, StreamPageParser
from range_param_type import RangeType

SESSION = requests.Session()


@click.group(help="Stream downloader for animeforce.org")
def main():
    pass


@main.command(name="search", help="Display search results from a query.")
@click.argument("query", nargs=-1)
def cmd_search(query):
    extract_search_results(" ".join(query))


@main.command(name="download", help="Download episodes from a search result.")
@click.option("--all", "_all", help="Whether to download all episodes available.",
              required=False, default=False, is_flag=True)
@click.option("--path", help="The path to download the files to.",
              type=click.Path(file_okay=False, exists=True, writable=True), default="./")
@click.option("--chunk-size", "chunk_size", help="The chunk size to stream in bytes, defaults to 4kb.",
              type=int, default=1024 * 4)
@click.option("--range", "-r", "_range", type=RangeType(), default=None,
              help="The range of episodes to download, must be formatted like so: start:end:step.\n"
                   "Defaults to downloading all episodes.")
@click.argument("query", nargs=-1)
def cmd_download(query, _all, path, chunk_size, _range):
    StreamDownloader.CHUNK_SIZE = chunk_size

    results = extract_search_results(" ".join(query))

    if len(results) == 1:
        ret = results[0]
        click.confirm(f"Going to download {ret[1]}, is that ok?", abort=True)
        to_download = ret
    else:
        prompt = click.prompt("Please pick a series by index", type=int)

        try:
            to_download = results[prompt - 1]
        except IndexError:
            click.echo("That index isn't present in the list.")
            return

    extract_direct_download_links(to_download[0], path, download_all=_all, episode_range=_range)


def extract_search_results(query: str) -> List[Tuple[str, str]]:
    qs = {
        "s": query,
        "cat": "6010"
    }

    results = list(reversed(SearchResultParser("https://ww1.animeforce.org", qs, SESSION).parse()))

    if not results:
        click.echo("No results found.")
        raise click.Abort()

    count = len(results)
    result_fmt = click.style(f"{count} {'results' if count > 1 else 'result'}", fg='green')
    click.echo(f"Found {result_fmt}, extracting data...")

    click.echo("-" * 20)
    click.echo()

    for index, (url, text) in enumerate(results, 1):
        click.echo(f"{click.style(str(index), fg='bright_blue')}. {text} ( {url} )")

    click.echo()
    click.echo("-" * 20)

    return results


def extract_direct_download_links(url: str, path: str, *, download_all: bool, episode_range: Optional[range]):
    click.echo("\nExtracting direct urls...")

    parser = StreamPageParser(url, SESSION)

    for title, url, is_downloadable in parser.parse(episode_range):
        episode = f"{click.style(str(title.replace('Episodio', 'Episode')), fg='bright_blue'): <3}"

        # vvvvid or something friendly probably
        if not is_downloadable:
            click.echo(f"{episode}"
                       f"is {click.style('not', fg='red')} downloadable -> {url}")
            continue

        actual_url = parser.get_episode_direct_url(url)

        if actual_url is None:
            click.echo("No other episodes available for download, exiting.")
            raise click.Abort()

        click.echo(f"{episode} -> {actual_url}")

        downloader = StreamDownloader(SESSION, actual_url, path)

        def do_download():
            try:
                downloader.download()
            except RuntimeError as exc:
                click.secho(str(exc), fg="red")

        if download_all:
            do_download()
            continue

        if click.confirm(
                "Would you like to download this episode? (pass the --all option when starting to download all)"
        ):
            do_download()


if __name__ == "__main__":
    try:
        main()
    finally:
        SESSION.close()
