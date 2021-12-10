from src.backend.metadata.TorrentParser import TorrentParser

data = TorrentParser.parse_filepath("../data/all/Free Solo Documentary (2018).torrent")

def iterate_tree(root_node, depth=0):
    print("  " * depth + root_node.name, root_node.length)
    if root_node.children:
        for child in root_node.children:
            iterate_tree(child, depth=depth+1)
            
iterate_tree(data.files)
