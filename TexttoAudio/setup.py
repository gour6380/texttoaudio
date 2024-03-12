from setuptools import setup, find_packages

setup(
    name="TexttoAudio",
    version="0.1",
    packages=find_packages(),
    description="A Text to Audio",
    long_description="Long",
    long_description_content_type="text/markdown",
    author="Gourav Karwasara",
    author_email="gourav@karwasara.com",
    url="https://github.com/gour6380/your_library",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # List your project dependencies here
        # 'dependency==version',
        'pydub==0.25.1',
        'requests==2.31.0'
    ],
)
