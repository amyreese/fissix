from setuptools import find_packages, setup

with open("README.md") as f:
    readme = f.read()


setup(
    name="fissix-py35",
    description="Backport of lib2to3, with enhancements",
    long_description=readme,
    long_description_content_type="text/markdown",
    version="19.3",
    author="John Reese",
    author_email="john@noswap.com",
    url="https://github.com/orsinium/fissix-py35",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
    ],
    license="PSF",
    install_requires=["appdirs"],
    setup_requires=["setuptools>=38.6.0"],
    packages=find_packages(exclude=["tests", "*.tests"]),
    package_data={"fissix": ["*.txt"]},
)
