from setuptools import find_packages
from setuptools import setup

from boomblazer.version import VERSION_STR

setup(
    name="Boomblazer",
    version=VERSION_STR,
    description="Game inspired by bomberman",
    author="Sylvain Marcuzzi, Lucas Perez",
    url="https://github.com/RLStrug/Boomblazer",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            #"boomblazer = boomblazer.__main__",
            "boomblazer-server = boomblazer.server:main",
            "boomblazer-cli = boomblazer.ui.cli:main",
            "boomblazer-ncurses = boomblazer.ui.ncurses:main",
        ]
    }
)
