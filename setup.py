import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

name = "httpsweet"

setuptools.setup(
    name=name,
    version="0.0.1",
    author="Eloy Pérez González",
    author_email="zer1t0ps@protonmail.com",
    description="An HTTP server for download and upload files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Zer1t0/" + name,
    scripts=[name],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
