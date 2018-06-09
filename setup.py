from setuptools import setup, find_packages

with open("README.md") as f:
    readme = f.read()

with open("fissix/__init__.py") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]

setup(
    name="fissix",
    description="Backport of lib2to3, with enhancements",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=version,
    author="John Reese",
    author_email="john@noswap.com",
    url="https://github.com/jreese/fissix",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    license="PSF License",
    setup_requires=["setuptools>=38.6.0"],
    packages=find_packages(exclude=["tests", "*.tests"]),
)
