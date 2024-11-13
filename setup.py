# setup.py
from setuptools import setup, find_packages

setup(
    name='commitgen',
    version='0.1.0',
    description='A CLI tool for generating conventional commit messages',
    author='kaizendae',
    author_email='abdelattie@gmail.com',
    url='https://github.com/kaizendae/commitgen',  # Link to your project repo
    packages=find_packages(),
    install_requires=[
        'gitpython>=3.1.0',
        'requests>=2.28.0'
    ],
    entry_points={
        'console_scripts': [
            'commitgen=commitgen.cli:main',  # Register the CLI command
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    package_data={
        'commitgen': ['prompt.txt'],
    },
)