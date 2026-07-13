import re
from setuptools import setup

with open("pdsk_util.py") as f:
    version = re.search(r'^__version__\s*=\s*["\'](.+)["\']', f.read(), re.M).group(1)

setup(
    name="pdsk-util",
    version=version,
    description="A beautiful disk usage viewer in python",
    author="Mixer",
    py_modules=["pdsk_util"],
    install_requires=[
        "rich",
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "pdsk-util=pdsk_util:main",
        ],
    },
    python_requires=">=3.6",
)
