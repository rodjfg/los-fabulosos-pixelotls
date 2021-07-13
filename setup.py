import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="los_fabulosos_pixelotls",
    version="0.0.1",
    author="Adrian Palacios Munoz",
    author_email="adpala93@gmail.com",
    description="toolkit for NMA2021 project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rodjfg/los-fabulosos-pixelotls.git",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[],
    include_package_data=True,
    zip_safe=False
)
