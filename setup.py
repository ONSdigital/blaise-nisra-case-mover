import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    version="1",
    description="Copy survey instruments from NISRA SFTP server to GCP storage bucket",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ONSdigital/blaise-nisra-case-mover",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
