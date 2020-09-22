import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mma",
    version="1.2.20.02",
    author="Hugo Neves de Carvalho",
    author_email="hugonvsc@gmail.com",
    description="MMA - Music Midi Accompaniment available as a pip module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hugonxc/mma_pip",
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points ={ 
        'console_scripts': [ 
            'mma = mma.mma:cli'
        ] 
    }, 
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)