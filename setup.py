from setuptools import setup

setup(
    name="pdsk-util",
    version="0.0.1",
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