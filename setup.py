from setuptools import setup

APP = ['main.py']
DATA_FILES = []
OPTIONS = {
    'optimize': 2,
    'includes': ['wx', 'pyperclip'],
    'excludes': ['numpy', 'gtk'],
    'plist': {
        'CFBundleName': 'Translators',
    },
    'arch': 'x86_64',
    'iconfile': 'icon.icns'
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
