from setuptools import find_packages, setup

NAME = 'spc-io'
VERSION = '0.0.0'
DESCRIPTION = ''
LONG_DESCRIPTION = ''
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
URL = 'https://github.com/h2020charisma/spc-io'
AUTHOR = 'IDEAconsult Ltd.'
AUTHOR_EMAIL = 'dev-charisma@ideaconsult.net'
LICENSE = ''

KEYWORDS = []

PYTHON_REQUIRES = '>=3.8'

PACKAGES = find_packages(where='code')

PACKAGE_DIR = {'': 'code'}

PACKAGE_DATA = {}

DATA_FILES = []

INSTALL_REQUIRES = [
        "numpy",
]

CLASSIFIERS = []


def setup_package():
    setup(
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        classifiers=CLASSIFIERS,
        data_files=DATA_FILES,
        description=DESCRIPTION,
        install_requires=INSTALL_REQUIRES,
        keywords=KEYWORDS,
        license=LICENSE,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
        name=NAME,
        package_dir=PACKAGE_DIR,
        packages=PACKAGES,
        python_requires=PYTHON_REQUIRES,
        url=URL,
        version=VERSION,
    )


if __name__ == '__main__':
    setup_package()
