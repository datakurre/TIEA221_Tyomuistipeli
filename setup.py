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
        "zope.interface",

        "pyramid",
        "pyramid-zcml",
        "pyramid-zodbconn",
        "pyramid-tm",  # (transaction manager)
    ],
    entry_points="""\
    [paste.app_factory]
    main = working_memory_games:main
    """,
)
