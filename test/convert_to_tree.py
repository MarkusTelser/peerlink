d = {
    "files": [
        {"length": 2, "path": ["urur", "uru2", "uru3", "second.png"]},
        {"length": 31, "path": ["RARBG.txt"]},
        {"length": 1, "path": ["Sample", "gua-freesolo-2160p-sample.mkv"]},
        {"length": 2, "path": ["Sample", "test", "gua-freesolo-2160p-sample.mkv"]},
        {"length": 3, "path": ["Sample", "test", "second.png"]},
        {"length": 15, "path": ["gua-freesolo-2160p.mkv"]},
        {"length": 11, "path": ["gua-freesolo-2160p.nfo"]},
    ]
}


class TorrentFile:
    def __init__(self, name="", length=0, encoding=None, checksum=None):
        self.name = name
        self.length = length
        self.encoding = encoding
        self.checksum = checksum
        
        self.children = list()
        
    def add_child(self, children: list):
        self.children.append(children)


def gen_tree_chain(filepath: list[str], end_node: TorrentFile):
    if len(filepath) > 1:
        folder_node = TorrentFile(filepath[0])
        folder_node.add_child(gen_tree_chain(filepath[1:], end_node))
        return folder_node
    elif len(filepath) == 1:
        end_node.name = filepath[0]
        return end_node
    else:
        return []


def add_node(root_node, path_list, end_node):
    if len(path_list) > 0:
        for child in root_node.children:
            # iterate deeper, until we can add node
            if child.name == path_list[0]:
                add_node(child, path_list[1:], end_node)
                return root_node
    
    # add child node to root node
    child = gen_tree_chain(path_list, end_node)
    root_node.add_child(child)


def iterate_over_files():
    files = d["files"]
    
    for file in files:
        # safe data for 
        data_node = TorrentFile()
        data_node.length = file["length"]
        
        add_node(root_dir, file["path"], data_node)

def calc_folder_size(root_node):
    if root_node.children:
        sum = 0
        for child in root_node.children:
            sum += calc_folder_size(child)
        root_node.length = sum
        return sum
    else:
        return root_node.length

def iterate_tree(root_node, depth=0):
    print("  " * depth + root_node.name, root_node.length)
    if root_node.children:
        for child in root_node.children:
            iterate_tree(child, depth=depth+1)


root_dir = TorrentFile("/")          
iterate_over_files()
calc_folder_size(root_dir)
iterate_tree(root_dir)