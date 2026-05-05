from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    'images',
    'audio',
    'installer.iss'
]
OPTIONS = {
    'iconfile': 'images/minesweeper.icns',
    'packages': ['cmu_graphics', 'PIL'],
    'includes': ['pygame'],
}

setup(
    name='Minesweeper',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
