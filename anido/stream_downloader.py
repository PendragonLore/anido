# -*- coding: utf-8 -*-

import pathlib
import typing
import urllib.parse

import requests
from tqdm import tqdm

from .utils import AtomicFile


class MaybeProgressBar(tqdm):
    def __init__(self, *args, **kwargs):
        self.actually_show: bool = kwargs.pop("actually_show")
        super().__init__(*args, **kwargs)

    def __enter__(self):
        if self.actually_show:
            return self
        return type("dummy", (), {"update": lambda *args, **kwargs: None})

    def __exit__(self, *args, **kwargs):
        if self.actually_show:
            super().__exit__(*args, **kwargs)


class StreamDownloader:
    __slots__ = ("session", "url", "filename", "path")

    CHUNK_SIZE: int = 1024 * 4

    def __init__(self, session: requests.Session, url: str, path: str):
        self.session: requests.Session = session
        self.url: str = url
        self.filename: typing.Optional[str] = None
        self.path: str = path

    def stream(self, show_progress: bool = True) -> typing.Iterator[bytes]:
        with self.session.get(self.url, stream=True) as response:
            with MaybeProgressBar(
                    actually_show=show_progress, total=int(response.headers["content-length"]),
                    unit_scale=True, unit_divisor=1024, unit="B", ncols=100
            ) as progress_bar:
                for chunk in response.iter_content(self.CHUNK_SIZE):
                    yield chunk
                    progress_bar.update(len(chunk))

    def download(self, show_progress: bool = True):
        with AtomicFile(self.prepare_file(), "wb") as file:
            for chunk in self.stream(show_progress=show_progress):
                file.write(chunk)

    def prepare_file(self) -> pathlib.Path:
        filename = urllib.parse.urlparse(self.url).path.split("/")[-1]
        file = pathlib.Path(self.path, filename)

        try:
            file.touch(exist_ok=False)
        except FileExistsError:
            raise RuntimeError(f"File {filename} already exists, won't overwrite it.")

        return file
