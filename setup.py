from setuptools import find_packages
from setuptools import setup

from .boomblazer.version import GAME_NAME
from .boomblazer.version import VERSION_STR

setup(
    name=GAME_NAME,
    version=VERSION_STR,
    description="Game inspired by bomberman",
    author="Sylvain Marcuzzi, Lucas Perez",
    url="https://github.com/RLStrug/Boomblazer",
    license="GNU Affero GPL3",
    keywords="game multiplayer network bomberman",
    packages=find_packages(),
    install_requires=[
        "windows-curses>=2.3.0; platform_system=='Windows'",
    ],
    python_requires=">3.5",
    entry_points={
        "console_scripts": [
            "boomblazer-server = boomblazer.network.server:main",
            "boomblazer-cli = boomblazer.ui.cli:main",
            "boomblazer-ncurses = boomblazer.ui.ncurses:main",
        ]
    }
)
