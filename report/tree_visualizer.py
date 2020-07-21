import networkx as nx
import matplotlib.pyplot as plt
import re
import pandas as pd
import collections
from PIL import Image
def get_collection_members(df, collection_tree, collection, collectionCSVNamesToName):   
    children = []
    regex = r"^info:fedora/(.*):(.*)$"
    is_collection_member =  df['isMemberOfCollection'] == collection
    member_list = df[is_collection_member]
        
    ## Loop through each member, if it is a collection model, then call this again!
    for index, row in member_list.iterrows():
        pid = row["PID"]
        cmodel = row["cmodel"]
        child = {}
        if cmodel == "info:fedora/islandora:collectionCModel":
            child["name"] = pid
            child["parent"] = collection
            fullPID = "info:fedora/"+pid
            collection_tree = get_collection_members(df, collection_tree, fullPID, collectionCSVNamesToName)
            if collection not in collectionCSVNamesToName:
                collection_name = re.search(regex, collection).group(1).capitalize()+" "+re.search(regex, collection).group(2)
            else:
                collection_name = collectionCSVNamesToName[collection]
            if fullPID not in collectionCSVNamesToName:
                print(fullPID)
                fullPIDName = re.search(regex, fullPID).group(1).capitalize()+" "+re.search(regex, fullPID).group(2)
                collectionCSVNamesToName[fullPID] = fullPIDName
            else:
                fullPIDName = collectionCSVNamesToName[fullPID]
            tup2 = (collection_name, fullPIDName);
            collection_tree.append(tup2)
        
    return collection_tree
def OrderTreeByDepth(tree, depth = 0, dictByDepth = {}, parent = None):
    i = 0
    newDepth = depth + 1
    if tree != {}:
        dictByDepth[newDepth] = {}
    for key in tree.keys():
        if parent != None:
            coords = dictByDepth[depth][parent]
        else:
            coords = []
        dictByDepth[newDepth][key] = coords[:]
        dictByDepth[newDepth][key].append(i)
        dictByDepth = OrderTreeByDepth(tree[key], newDepth, dictByDepth, key)
        i+=1
    return dictByDepth

def GetNodesWithNoChildren(tree, parent = None, noChildren = []):
    if tree == {}:
        noChildren.append(parent)
    else:
        for key in tree.keys():
            noChildren = GetNodesWithNoChildren(tree[key], key, noChildren)
    return noChildren

def DefineNode(nodeName, nodeX, nodeY, G, pos):
    textOffset = 0.02
    G.add_node(nodeName)
    pos[nodeName] = (nodeX, nodeY)
    plt.text(nodeX+textOffset,nodeY,s=nodeName, horizontalalignment='center',verticalalignment='center', rotation = 'vertical')

def CreateTree(tree):
    plt.figure(figsize = (17,13), dpi = 100)
    G=nx.Graph()
    x = 0
    y = 0
    for root in tree.keys():
        pos = {}
        DefineNode(root, x, y, G, pos)
        BuildTree(G, tree[root], root, pos)
    nx.draw(G, pos = pos, node_size = 300)
    plt.savefig('treeTest.png')
    img = Image.open("treeTest.png")
    rotated = img.transpose(Image.ROTATE_270)
    rotated.save('treeTestTranspose.png')

def BuildTree(G, tree, parent, pos, spaceX = 2):
    spaceY = -1
    #pastParent = False
    #for node in tree.keys():
    #    if node != parent:
    increment = spaceX/(len(tree.keys()))
    startX = pos[parent][0]-spaceX/2+increment/2
    startY = pos[parent][1] + spaceY
    i = 0
    for node in tree.keys():
        DefineNode(node, startX+increment*i, startY, G, pos)
        G.add_edge(parent, node)
        if tree[node] != {}:
            G = BuildTree(G, tree[node], node, pos, increment)
        i+=1
    return G

def ConstructTreeDict(df, collectionCSVNamesToName):
    tree = lambda: collections.defaultdict(tree)
    collection_tree = tree()
    collection = "info:fedora/dsu:root"
    path_list = ["root"]
    collection_tree =[]
    ## Build child parent tuple tree, recursively
    collection_tree = get_collection_members(df, collection_tree, collection, collectionCSVNamesToName)
    lst = collection_tree

    # Build a directed graph and a list of all names that have no parent
    graph = {name: set() for tup in lst for name in tup}
    has_parent = {name: False for tup in lst for name in tup}
    for parent, child in lst:
        graph[parent].add(child)
        has_parent[child] = True

    # All names that have absolutely no parent:
    roots = [name for name, parents in has_parent.items() if not parents]

    # traversal of the graph (doesn't care about duplicates and cycles)
    treeData = []
    def traverse(hierarchy, graph, names):
        for name in names:
            hierarchy[name] = traverse({}, graph, graph[name])
        return hierarchy
    return traverse({}, graph, roots)
