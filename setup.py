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
    install_requires=["aiohttp"],
    classifiers=[
        "Development Status :: 3 - Alpha",  # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Intended Audience :: Developers",
        "Topic :: Home Automation",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
    ],
)
