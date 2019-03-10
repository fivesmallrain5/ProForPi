import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Five",
    version="0.0.1",
    author="fivesmallrain",
    author_email="author@example.com",
    description="my own package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fivesmallrain5/Five",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

