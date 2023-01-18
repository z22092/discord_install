from os.path import join
from tarfile import open
from typing import IO

DEFAULT_MODE = "r:gz"


def extract(
    file: IO, path: str = None, includes: list[str] = [], excludes: list[str] = []
):
    with open(mode=DEFAULT_MODE, fileobj=file) as tar:
        files = tar.getmembers()

        root_dir = files.pop(0)
        tar.extract(root_dir, path)

        if includes or excludes:
            inc = tuple([join(root_dir.name, i) for i in includes])
            exc = tuple([join(root_dir.name, i) for i in excludes])

            for member in files:
                if member.name.startswith(inc) and not member.name.startswith(exc):
                    tar.extract(member, path)
        else:
            tar.extractall(path, members=files)

        return join(path, root_dir.name)
