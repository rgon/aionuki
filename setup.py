from setuptools import find_packages, setup


setup(
    name="aionuki",
    version="2.0.0",
    license="GPL3",
    description="Asynchronous python bindings for nuki.io bridges.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Gonzalo Ruiz",
    url="https://github.com/rgon/aionuki",
    packages=find_packages(),
    install_requires=["requests"],
)
