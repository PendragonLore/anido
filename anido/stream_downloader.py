# -*- coding: utf-8 -*-

import pathlib
import shutil
import tempfile
import urllib.parse

from tqdm import tqdm


class MaybeProgressBar(tqdm):
    def __init__(self, *args, **kwargs):
        self.actually_show = kwargs.pop("actually_show")
        super().__init__(*args, **kwargs)

    def __enter__(self):
        if self.actually_show:
            return self
        return type("dummy", (), {"update": lambda *args, **kwargs: None})

    def __exit__(self, *args, **kwargs):
        if self.actually_show:
            super().__exit__(*args, **kwargs)


class StreamDownloader:
    CHUNK_SIZE = 1024 * 4

    def __init__(self, session, url):
        self.session = session
        self.url = url
        self.filename = None

    def stream(self, show_progress=True):
        with self.session.get(self.url, stream=True) as response:
            with MaybeProgressBar(
                    actually_show=show_progress, total=int(response.headers["content-length"]),
                    unit_scale=True, unit_divisor=1024, unit="B", ncols=100
            ) as bar:
                for chunk in response.iter_content(self.CHUNK_SIZE):
                    yield chunk
                    bar.update(len(chunk))

    def download(self):
        file = self.prepare_file()

        with tempfile.NamedTemporaryFile("wb") as ftemp:
            for chunk in self.stream():
                ftemp.write(chunk)

            shutil.copy2(ftemp.name, file.name)

    def prepare_file(self):
        filename = urllib.parse.urlparse(self.url).path.split("/")[-1]
        file = pathlib.Path(filename)

        try:
            file.touch(exist_ok=False)
        except FileExistsError:
            raise RuntimeError(f"File {filename} already exists, won't overwrite it.")

        return file