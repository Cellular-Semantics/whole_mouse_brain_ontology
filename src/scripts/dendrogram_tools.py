import warnings
import json


def read_json_file(file_path):
    """
    Read json file from the given path.
    Args:
        file_path: The path to the json file.

    Returns: The json object.
    """
    with open(file_path, "r") as f:
        return json.load(f)

def cas_json_2_nodes_n_edges(path_to_json):
    j = read_json_file(path_to_json)
    out = {}
    tree_recurse(j, out)
    return out


def tree_recurse(tree, out):
    """Convert CAS JSON to a list of nodes and edges, where nodes are
    Copies of nodes in CAS JSON & edges are duples - (subject(child), object(parent))
    identified by 'cell_set_accession'.

    Args:
        - Tree: CAS JSON, or some subtree of it
        - Output structure to populate (starting point must be an empty dict)
    """
    if not out:
        out['nodes'] = []
        out['edges'] = set()
    ranked_labelsets = [labelset["name"] for labelset in tree['labelsets'] if "rank" in labelset]
    for annotation in tree['annotations']:
        if annotation['labelset'] in ranked_labelsets:
            node = annotation.copy()
            out['nodes'].append(node)
            out['edges'].add((node['cell_set_accession'], node.get('parent_cell_set_accession', '')))
    # if 'node_attributes' in tree.keys():
    #     if len(tree['node_attributes']) > 1:
    #         warnings.warn("Don't know how to deal with multiple nodes per recurse")
    #     ID = tree['node_attributes'][0]['cell_set_accession']
    #
    #     out['nodes'].append(tree['node_attributes'][0])
    #     if parent_node_id:
    #         out['edges'].add((ID, parent_node_id))
    #     if 'children' in tree.keys():
    #         for c in tree['children']:
    #             tree_recurse(c, out, parent_node_id=ID)
    #     else:
    #         warnings.warn("non leaf node %s has no children" % ID)
    # elif 'leaf_attributes' in tree.keys():
    #     if len(tree['leaf_attributes']) > 1:
    #         warnings.warn("Don't know how to deal with multiple nodes per recurse")
    #     ID = tree['leaf_attributes'][0]['cell_set_accession']
    #     # Tag leaves
    #     tree['leaf_attributes'][0]['is_leaf'] = True
    #     out['nodes'].append(tree['leaf_attributes'][0])
    #     out['edges'].add((ID, parent_node_id))
    #     if 'children' in tree.keys():
    #         warnings.warn('leaf node %s has children!' % ID)
    # else:
    #     warnings.warn("No recognized nodes")
