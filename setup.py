import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'redis',
    'pyramid',
    'pyramid_debugtoolbar',
    'waitress',
    ]

setup(name='oest',
      version='0.1',
      description='Online Estimate - Web Service and Supporting Modules',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Nicholas Long',
      author_email='nick@studiocoda.com',
      url='https://github.com/adoc',
      keywords='oest online estimate web',
      packages=['oest', 'thredis', 'safedict'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="tests",
      entry_points="""\
      [paste.app_factory]
      main = service:main
      """,
      )
