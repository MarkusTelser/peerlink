from setuptools import setup, find_packages

setup(
    name="peerlink",
    version="0.1",
    license="GPL v3.0",
    author="Markus Telser",
    author_email="markus.telser99@gmail.com",
    url="https://github.com/MarkusTelser/peerlink",
    description="bittorrent client from scratch for linux, mac, win",
    long_description=''.join(open('README.md', 'r').readlines()),
    long_description_content_type="text/markdown",
    keywords=['bittorrent', 'torrent', 'client'],
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[], # define after testing versions
    package_data={  # Optional
       
    },
    entry_points={
        'console_scripts': [
            'peerlink=main:start'
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/MarkusTelser/peerlink/issues',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://saythanks.io/to/MarkusTelser',
        'Source': 'https://github.com/MarkusTelser/peerlink',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Topic :: Communications :: File Sharing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        "Programming Language :: Python :: 3.10",
        'Programming Language :: Python :: 3 :: Only',
    ],
)