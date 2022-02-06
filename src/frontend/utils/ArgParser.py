from PyQt6.QtCore import QSettings
from os.path import dirname, exists, isfile, splitext
from argparse import ArgumentParser
import sys

from src.backend.metadata.MagnetLink import MagnetLink
from src.backend.metadata.TorrentParser import TorrentParser

def args_parser():
    prog = "peerlink"
    description = "client written in python that implements the bittorrent protocol from scratch"
    usage = "peerlink [options] [(<file-path> | <magnet-link>)]"
    
    parser = ArgumentParser(prog, description=description, usage=usage, add_help=False)
    
    arg_opts = parser.add_argument_group('args (mutually exclusive)')
    args_opt = arg_opts.add_mutually_exclusive_group()
    args_opt.add_argument('-p', metavar="FILE-PATH")
    args_opt.add_argument('-m', metavar="MAGNET-LINK")

    options = parser.add_argument_group('options')
    options.add_argument('-a', '--author', help="show author information", action="store_true")
    options.add_argument('-l', '--license', help="show license terms", action="store_true")
    options.add_argument('-v', '--version', help="show program version", action="store_true")
    options.add_argument('-r', '--repository', help="output source git repository url", action="store_true")
    options.add_argument('-c', '--config', help="output local application config path", action="store_true")
    options.add_argument('-h', '--help', help="show this help message and exit", action="store_true")
    
    group_opt = parser.add_argument_group('torrent options')
    group_opt.add_argument('--save-path', help="path where downloaded files are saved", metavar="PATH", action="store")
    group_opt.add_argument('--category', help="sets existing or new category for torrent", action="store")
    group_opt.add_argument('--pad-files', help="fill all files with null bytes", action="store_true")
    group_opt.add_argument('--dont-autostart', help="doesn't start torrent after adding to list", action="store_true")
    group_opt.add_argument('--dont-check-pieces', help="pieces aren't compared with hash for integrity", action="store_true")
    group_opt.add_argument('--download-strategy', choices=['rarest-first(default)', 'sequential', 'random'], default='rarest-first')
    args = parser.parse_args()

    if args.help:
        print(parser.format_help(), end="")
        sys.exit()
    
    args = vars(args)
    
    if not args['p'] and not args['m']:
        optional_par = False
        if args['author']:
            print('the author of this software is Markus Telser')
            optional_par = True
        if args['license']:
            print(open('LICENSE.txt').read(), end="")
            optional_par = True
        if args['version']:
            print('peerlink 0.1 beta')
            optional_par = True
        if args['repository']:
            print('https://github.com/MarkusTelser/fastlink')
            optional_par = True
        if args['config']:
            print(dirname(QSettings().fileName()))
            optional_par = True
        if optional_par:
           sys.exit()
    
    return parser

def args_torrent(parser):
    torrents = list()
    
    args = vars(parser.parse_args())
    
    # check if valid path, else throw error
    if args['p']:
        if not exists(args['p']):
            parser.error('path doesnt exist')
        if not isfile(args['p']):
            parser.error('path is not a file')
        if not splitext(args['p'])[1] == '.torrent':
            parser.error('file is not a torrent')
        
        torrent = TorrentParser.parse_filepath(args['p'])
        extras = dict()
       
        extras['pad_files'] = args['pad_files']
        extras['start'] = not args['dont_autostart']
        extras['check_hash'] = not args['dont_check_pieces']
        extras['strategy'] = args['download_strategy']
        if args['save_path'] != None:
            extras['path'] = args['save_path']
        if args['category'] != None:
            extras['category'] = args['category']
        
        torrents.append((torrent, extras))
            
    return torrents
            
def args_magnet(parser):
    magnets = list()
    args = parser.parse()
    
    # check if valid magnet link, else throw error
    if args['m']:
        try:
            MagnetLink().parse(args['m'])
        except Exception as e:
            parser.error(str(e))
    
    return magnets