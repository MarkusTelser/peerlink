import PyInstaller.__main__
from __version__ import __version__

params = [
    '--noconfirm',
    '--onefile',
    '--windowed',
    '--name', 'peerlink' + __version__,
    '--add-data', '/home/carlos/Code/Python/peerlink/resources:resources/',
    '--add-data', '/home/carlos/Code/Python/peerlink/LICENSE.txt:.',
    '--icon', '/home/carlos/Code/Python/peerlink/resources/logo.ico',
    'main.py'
]

PyInstaller.__main__.run(params)
