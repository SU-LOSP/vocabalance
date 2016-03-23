from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='vocabalance',
    version='0.1.0',
    description='Tool for analysing character word biases in Shakespeare plays',
    url='https://gitlab.sphalerite.org/linus/vocabalance',
    author='Linus Heckemann',
    author_email='linus.heckemann.2014@uni.strath.ac.uk',
    license='GPLv3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Education',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
    ],
    keywords='shakespeare vocabulary statistics',
    modules='vocabalance',
    install_requires=['beautifulsoup4'],
    entry_points={
        'console_scripts': [
            'vocabalance=vocabalance:main',
        ],
    },
)
