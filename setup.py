import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    version="0.0.1",
    description="A package to copy survey files using SFTP connection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ONSdigital/Blaise_NISRA_Case_Mover_SFTP",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)