import hou
import sys
import os
import string

prefix = "    "

dirsubs = { "chop":"CHOP", 
            "cop2":"COP2",
            "dop": "DOP",
            "lop": "LOP",
            "obj": "OBJ",
            "out": "ROP",
            "pop": "POP", 
            "shop":"SHOP",
            "sop": "SOP",
            "vex": "VEX",
            "vop": "VOP",
            "top": "TOP" }

catsubs = { "chop":"Chop", 
            "cop2":"Cop2", 
            "dop": "Dop",
            "lop": "Lop",
            "obj": "Object", 
            "out": "Driver", 
            "pop": "Particle", 
            "shop":"Shop", 
            "sop": "Sop", 
            "vex": "VopNet", 
            "vop": "Vop",
            "top": "Top" }


def writeHeader(helpfile, node, nodename, context):
    helpfile.write("#type:     node\n")
    helpfile.write("#context:  " + context + "\n")
    helpfile.write("#internal: " + nodename + "\n")
    dirname = context
    if(context in dirsubs): 
        dirname = dirsubs[context]
    helpfile.write("#icon:     " + dirname + "/" + nodename + "\n")
    helpfile.write("#tags:     sidefxedu\n")
    helpfile.write("\n= " + node.description() + " =\n")
    helpfile.write("\n\"\"\"Summary.\"\"\"\n\n")
    helpfile.write("\nWARNING:\n")
    helpfile.write(prefix + "This node is made for education purposes only. You can use it for other things, but at your own risks.\n")
    helpfile.write("[Image:/images/sidefxedu_full.png]\n\n")
    # helpfile.write(":video:\n")
    # helpfile.write(prefix + "#src:/movies/cablegenerator.mp4\n\n")
    helpfile.write("<Description goes here>\n\n\n")
    helpfile.write("@parameters\n\n")


def writeFooter(helpfile):
    helpfile.write("@locals\n    \n    \n")
    helpfile.write("@related\n")
    helpfile.write("- [item | /link ]\n")
    helpfile.write("\n")


#recursive for nested folders.
def writeTemplates(helpfile, templates, indent):
    for temp in templates:
        if(temp.type() == hou.parmTemplateType.Separator or
           temp.type() == hou.parmTemplateType.Label) or temp.isHidden():
            continue

        if(temp.type() == hou.parmTemplateType.Folder):
            helpfile.write(prefix + indent + " " + temp.label() + " " + indent +"\n\n")
            writeTemplates( helpfile, temp.parmTemplates(), "===" )
        else:
            if(len(temp.label()) > 0):
                helpfile.write(prefix + temp.label() + ":\n")
                helpfile.write(prefix + prefix + "#id: " + temp.name() + "\n")
                helpfile.write(prefix + prefix + "\n")

            if(temp.type() == hou.parmTemplateType.Menu):
                for i in range(len(temp.menuLabels())):
                    helpfile.write(prefix + prefix + temp.menuLabels()[i] 
                                     + ":\n"+prefix + prefix+ prefix+"\n")

                
def create_node_help(nodetypename, context, directory):

    if context not in catsubs.keys():
        raise hou.NodeError("Specified context not found. Available contexts: {}".format([x + " " for x in catsubs.keys()]))

    table = hou.nodeTypeCategories()[ catsubs[context] ]

    if nodetypename not in table.nodeTypes().keys():
        raise hou.NodeError("Specified node type does not exist.")

    node = table.nodeTypes()[ nodetypename ]
    
    namecomponents = node.nameComponents()
    txtname = namecomponents[1]+"--"+namecomponents[2]

    if namecomponents[3] != "":
        txtname += "-"+namecomponents[3]
    txtname += ".txt"

    helpfile = os.path.join(hou.text.expandString(directory), txtname)
    with open(helpfile,'w') as f:
        writeHeader(f, node, nodetypename, context)
        writeTemplates(f, node.parmTemplateGroup().entries(), "==")
        writeFooter(f)


def create_node_help_auto(node):

    if node:

        node_type_name = node.type().name()

        category_name = node.type().category().name()
        node_context = 'sop'  # Default value

        for context, name in catsubs.items():
            if name == category_name:
                node_context = context
                break
    
        node_directory = '$SIDEFXEDU/help/nodes/{0}/'.format(node_context)

        create_node_help(node_type_name, node_context, node_directory)


    return
