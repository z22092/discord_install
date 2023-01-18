import ssl

ssl._create_default_https_context = ssl._create_unverified_context

import subprocess
import platform

from os import makedirs, symlink, sep, getuid, environ
from os.path import join, expanduser, abspath, dirname
from sys import argv, exit, executable

from pathlib import Path


from tar import extract
from request import request

DEFAULT_VERSION = "0.0.24"

NAME = "discord"
APP = "Discord"
SUMMARY = "All-in-one voice and text chat for gamers"

VERSION = environ.get("DISCORD_VERSION", DEFAULT_VERSION)
FILENAME = f"{NAME}-{VERSION}.tar.gz"
SOURCE = f"https://dl.discordapp.net/apps/linux/{VERSION}/{FILENAME}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"
}

USR_DIR = join(abspath(sep), "usr")

ICON = "discord.png"
SHORTCUT = "discord.desktop"

LOCAL_DIR = join(expanduser("~"), ".local")

LOCAL_SHARE_APP = lambda LOCAL_DIR=LOCAL_DIR: join(LOCAL_DIR, "share", "applications")
LOCAL_LIB_DIR = lambda LOCAL_DIR=LOCAL_DIR: join(LOCAL_DIR, "lib", NAME, VERSION)
LOCAL_SHARE_SHORTCUT = lambda LOCAL_DIR=LOCAL_DIR: join(
    LOCAL_SHARE_APP(LOCAL_DIR), SHORTCUT
)

USR_ICON_DIR = join(USR_DIR, "share", "icons")
USR_ICON = join(USR_ICON_DIR, ICON)
USR_APP = join(USR_DIR, "bin", APP)
USR_SHARE_APP = join(USR_DIR, "share", "applications")
USR_SHORTCUT = join(USR_SHARE_APP, SHORTCUT)

DESKTOP_SHORTCUT_TEMPLATE = f"""
[Desktop Entry]
Name={APP}
Comment={SUMMARY}
Exec={APP}
Type=Application
Terminal=false
Icon={USR_ICON}
Categories=Network;
"""

DEFAULT_OPEN_MODE = "w+"
BASE_COMMAND = ["/usr/bin/sudo", argv[0]]


IS_ROOT = getuid() == 0


class NotSudo(Exception):
    pass


def _require_sudo():
    if not IS_ROOT:
        raise NotSudo(
            "This program is not run as sudo or elevated this it will not work"
        )


def _run_command(
    command,
    *arguments,
) -> subprocess.Popen:
    return subprocess.Popen(
        [command, *arguments],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )


def _live_view(process: subprocess.Popen):
    while process.stdout.readable():
        line: str = process.stdout.readline()

        if not line:
            return process.stdout.read()

        print(line.strip())


def _delete_folder(pth: Path):
    for sub in pth.iterdir():
        if sub.is_dir():
            _delete_folder(sub)
        else:
            sub.unlink()
    pth.rmdir()


def _remove(file: str):
    try:
        pth = Path(file)
        if pth.is_dir():
            _delete_folder(pth)
        else:
            pth.unlink()
        print(f"remove {pth.__str__()}")
    except FileNotFoundError:
        return


def _create_symlink(src: str, dst: str):
    try:
        symlink(src, dst, False)
    except FileExistsError:
        pass


def uninstall(LOCAL_DIR: str = LOCAL_DIR):

    print(f"uninstall {NAME} {VERSION}")
    for path in [
        LOCAL_LIB_DIR(LOCAL_DIR),
        USR_ICON,
        LOCAL_SHARE_SHORTCUT(LOCAL_DIR),
        USR_SHORTCUT,
        USR_APP,
    ]:
        _remove(path)


def create_links(work_dir: str, LOCAL_DIR: str = LOCAL_DIR):
    print(f"start create files {NAME} {VERSION}")
    print(f"base work dir {work_dir}")

    local_share_shortcut = LOCAL_SHARE_SHORTCUT(LOCAL_DIR)

    makedirs(USR_ICON_DIR, exist_ok=True)
    _create_symlink(join(work_dir, ICON), USR_ICON)
    print(f"created {ICON} on {USR_ICON}")

    _create_symlink(join(work_dir, APP), USR_APP)
    print(f"created {APP} on {USR_APP}")

    makedirs(LOCAL_SHARE_APP(LOCAL_DIR), exist_ok=True)
    with open(local_share_shortcut, DEFAULT_OPEN_MODE) as shortcut:
        shortcut.write(DESKTOP_SHORTCUT_TEMPLATE)

    print(f"created {SHORTCUT} on {local_share_shortcut}")
    print(DESKTOP_SHORTCUT_TEMPLATE)

    makedirs(USR_SHARE_APP, exist_ok=True)
    _create_symlink(local_share_shortcut, USR_SHORTCUT)
    print(f"created {SHORTCUT} on {USR_SHORTCUT}")


def install(LOCAL_DIR: str = LOCAL_DIR):
    print(f"platform: {platform.platform()}")

    local_lib_dir = LOCAL_LIB_DIR(LOCAL_DIR)
    print(f"Start install {NAME} {VERSION} on {local_lib_dir}")

    if IS_ROOT:
        uninstall(LOCAL_DIR)
    else:
        _live_view(_run_command(*BASE_COMMAND, "uninstall", LOCAL_DIR))

    print(f"download {SOURCE}")
    response = request(SOURCE, headers=HEADERS)

    if response.status > 299:
        print(response.body)
        return

    work_dir = extract(file=response.get_raw(), path=local_lib_dir)
    print(f"download finish on folder {work_dir}")

    if IS_ROOT:
        create_links(work_dir, LOCAL_DIR)
    else:
        _live_view(_run_command(*BASE_COMMAND, "create_links", work_dir, LOCAL_DIR))


if __name__ == "__main__":
    if len(argv) == 1:
        install()
        exit(0)

    command = argv[1]
    if command == "uninstall":
        _require_sudo()
        uninstall(argv[2])
        exit(0)

    if command == "create_links":
        _require_sudo()
        create_links(argv[2], argv[3])
        exit(0)
