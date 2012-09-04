from setuptools import setup, find_packages

version = "1.0.0"
requires = [
    "zope.interface",

    "pyramid",
    "pyramid-zcml",
    "pyramid-zodbconn",
    "pyramid-tm",  # (transaction manager)
],

setup(
    name="kog-working-mem",
    version=version,
    description="Working memory training games",
    long_description=open("README.txt").read() + "\n" +
                     open("CHANGES.txt").read(),
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
    install_requires=requires,
    entry_points="""\
    [paste.app_factory]
    main = kog_working_mem:main
    """,
)
