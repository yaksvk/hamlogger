from distutils.core import setup

setup(
    name="Hamlogger",
    version="1.0.0",
    author="Jakub Ondrusek",
    author_email="yak@gmx.co.uk",
    packages=["lib"],
    include_package_data=True,
    url="",
    license="LICENSE",
    description="An amateur radio logging app",
    long_description=open("README").read(),
    install_requires=[
        "sqlalchemy",
    ],
)
