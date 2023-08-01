# from importlib import reload

def create_node_help(nodetypename, context, directory):
    from edu_opui import edu_docs
    # reload(edu_docs)
    edu_docs.create_node_help(nodetypename, context, directory)

def create_node_help_auto(node):
    from edu_opui import edu_docs
    # reload(edu_docs)
    edu_docs.create_node_help_auto(node)

