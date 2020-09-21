import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mma",
    version="0.0.1",
    author="Bob",
    author_email="author@example.com",
    description="I'm packing mma for my own propose ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hugonxc/mma_pip",
    packages=setuptools.find_packages(include=['mma.MMA.MMA*']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)