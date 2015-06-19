
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'markogen',
    'author': 'siolag161',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'pdthanh06@gmail.com',
    'version': '0.1',
    'install_requires': ['nose','six'],
    'packages': ['markogen'],
    'scripts': [],
    'name': 'markogen',
    'entry_points': {
          'console_scripts': [
              'markogen = markogen.__main__:main'
          ]
     },
}

setup(**config)
