import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="riemann-zyxel-gs1200",
    version="1",
    author="Martin Stensgård",
    author_email="mastensg@mastensg.net",
    description="Send metrics to Riemann from Zyxel GS1200 PoE switches.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mastensg/riemann-zyxel-gs1200",
    packages=setuptools.find_packages(),
    install_requires=[
        "bernhard >= 0.2.6",
        "pyjsparser >= 2.5.2",
        "requests >= 2.21.0",
        "schedule >= 0.6.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts":
        ["riemann-zyxel-gs1200 = riemann_zyxel_gs1200:__main__.main"],
    },
)
