import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="brs-py",
    version="0.5.1",
    author="Kevin Schroeder",
    author_email="Kmschr@gmail.com",
    description="Brickadia savefile reader/writer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.github.com/Kmschr/brs-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)