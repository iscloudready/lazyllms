from setuptools import setup, find_packages

setup(
    name="lazyllms",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'rich',
        'textual',
        'requests',
        'psutil',
        'pynvml',
        'pyyaml',
        'argparse',
    ],
)