from setuptools import setup, find_packages

setup(
    name="working-memory-games",
    version="1.0.0",
    description="Working memory training games",
    long_description=(open("README.rst").read() + "\n" +
                      open("CHANGES.rst").read()),
    # Get more strings from
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
    ],
    keywords="",
    author="",
    author_email="",
    url="",
    license="GPL",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",

        "zope.interface",
        "venusian",
        "pyramid",
        "pyramid_zodbconn",

        "pyramid_tm",  # (transaction manager)
        "zope.index",  # (index)

        "numpy",
    ],
    extras_require={'test': [
        'plone.testing',
        'robotframework-selenium2library',
        'robotsuite',
        'waitress',
        'webtest'
    ]},
    entry_points="""\
    [paste.app_factory]
    main = working_memory_games:main
    """,
)
