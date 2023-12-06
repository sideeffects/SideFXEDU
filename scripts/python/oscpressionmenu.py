from __future__ import print_function
from builtins import zip
import hou
import snippetmenu
import re

_hasloadedsnippets = False

_initialsnippets = {}
_oscsnippets = {}
_oscsnippets_sol = {}

_initialsnippets['oscilloscope/snippet'] = [
    "y = x",
    'Linear',
    "y = pow(x, 2)",
    'Quadratic | pow(x, 2)',
    "y = pow(x, 2) + pow(z, 2)",
    'Quadratic | pow(x, 2) + pow(z, 2)',
    "y = pow(x, 3)",
    'Cubic | pow(x, 3)',
    "y = pow(x, 3) + pow(z, 3)",
    'Cubic | pow(x, 3) + pow(z, 3)',
    "y = pow(x, a) + pow(z, b)",
    'Power | pow(x, a) + pow(z, b)',
    "y = log(x)",
    'Logarithmic',
    "y = exp(x)",
    'Exponential',
    "y = sin(x)",
    'Sine',
    "y = cos(x)",
    'Cosine',
    "y = tan(x)",
    'Tangent',
    "y = amp * sin(freq * x + phase) + offset",
    'Sine with parameters',
    "y = amp * cos(freq * x + phase) + offset",
    'Cosine with parameters',
    "y = sin(x) + cos(z)",
    'y = sin(x) + cos(z)',
]


def installInitialSnippets():
    """ Copies the initial snippets into _oscsnippets and adds
        the comment prefix.
    """
    for parm in _initialsnippets:
        rawlist = _initialsnippets[parm]
        pairlist = list(zip(rawlist[::2], rawlist[1::2]))
        item_list = []
        sol_list = []
        for (body, title) in pairlist:
            sol_list.append(body.strip())
            sol_list.append(title)
            # body = '// ' + title + '\n' + body
            body = body
            item_list.append(body)
            item_list.append(title)
        _oscsnippets[parm] = item_list
        _oscsnippets_sol[parm] = sol_list


def ensureSnippetsAreLoaded():
    global _hasloadedsnippets

    if not _hasloadedsnippets:
        _hasloadedsnippets = True
        installInitialSnippets()
        (snippets, snippets_sol) = snippetmenu.loadSnippets(
            hou.findFiles('OSCpressions.txt'), '//')
        _oscsnippets.update(snippets)
        _oscsnippets_sol.update(snippets_sol)


def buildSnippetMenu(snippetname):
    """ Given a snippetname, determine what
        snippets should be generated
    """
    ensureSnippetsAreLoaded()
    if snippetname in _oscsnippets:
        return list(_oscsnippets[snippetname])
    else:
        return ["", "None"]


def buildSingleLineSnippetMenu(snippetname):
    """ Given a snippetname, determine what
        snippets should be generated
    """
    ensureSnippetsAreLoaded()
    if snippetname in _oscsnippets_sol:
        return list(_oscsnippets_sol[snippetname])
    else:
        return ["", "None"]


# Strings representing channel calls
chcalls = [
    'ch', 'chf', 'chi', 'chu', 'chv', 'chp', 'ch2', 'ch3', 'ch4',
    'vector(chramp', 'chramp',
    'vector(chrampderiv', 'chrampderiv',
    'chs',
    'chdict', 'chsop'
]
# Expression for finding ch calls
chcall_exp = re.compile(f"""
\\b  # Start at word boundary
({"|".join(re.escape(chcall) for chcall in chcalls)})  # Match any call string
\\s*[(]\\s*  # Opening bracket, ignore any surrounding whitespace
('\\w+'|"\\w+")  # Single or double quoted string
[),]  # Closing bracket or comma marking end of first argument
""", re.VERBOSE)
# Number of components corresponding to different ch calls. If a call string is
# not in this dict, it's assumed to have a single component.
ch_size = {
    'chu': 2, 'chv': 3, 'chp': 4, 'ch2': 4, 'ch3': 9, 'ch4': 16,
}
# This expression matches comments (single and multiline) and also strings
# (though it will miss strings with escaped quote characters).
comment_or_string_exp = re.compile(
    r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
    re.DOTALL | re.MULTILINE
)


# This subsitution function replaces comments with spaces and leaves strings
# alone. This has the effect of skipping over strings so it doesn't get confused
# by comment characters inside a string.
def remove_comments(match):
    s = match.group(0)
    if s.startswith('/'):
        return ' '
    else:
        return s

def _addSpareParmsToStandardFolder(node, parmname, refs):
    """
    Takes a list of (name, template) in refs and injects them into the
    standard-named folder for generated parms.  If it doesn't exist,
    create the folder and place before parmname.
    """
    if not refs:
        return          # No-op

    # We consider a multiparm any parameter with a number in it.
    # This might have false positives, but it is important to not try
    # to create a parameter before a multiparm as that slot
    # won't exist.  We also use a single standard folder name
    # for all the multiparm snippets.
    ismultiparm = any(map(str.isdigit, parmname))

    ptg = node.parmTemplateGroup()
    foldername = 'folder_generatedparms_' + parmname
    if ismultiparm:
        foldername = 'folder_generatedparms'

    folder = ptg.find(foldername)
    if not folder:
        folder = hou.FolderParmTemplate(
            foldername,
            "Generated Channel Parameters",
            folder_type=hou.folderType.Simple,
        )
        folder.setTags({"sidefx::look": "blank"})
        if not ismultiparm:
            ptg.insertBefore(parmname, folder)
        else:
            ptg.insertBefore(ptg.entries()[0], folder)

    # Insert/replace the parameter templates
    indices = ptg.findIndices(folder)
    for name, template in refs:
        exparm = node.parm(name) or node.parmTuple(name)
        if exparm:
            ptg.replace(name, template)
        else:
            ptg.appendToFolder(indices, template)
    node.setParmTemplateGroup(ptg)

def createSpareParmsFromOCLBindings(node, parmname):
    """ 
    Parse the @BIND commands in an OpenCL kernel and create corresponding
    spare parameters
    """
    parm = node.parm(parmname)
    code = parm.evalAsString()

    # Extract bindings
    bindings = hou.text.oclExtractBindings(code)

    channellinks = []
    ramplinks = []
    refs = []

    # Sadly, SOP and DOP opencl have completely different
    # binding names.  Use the base bindings type to differntiate
    if node.parm('bindings') is not None:
        # SOP based (also COP)
        bindparm = 'bindings'
        bindparmprefix = 'bindings'
        bindparmsuffix = {
            'name' : '_name',
            'type'   : '_type',
            'ramp' : '_ramp',
            'ramptype' : '_ramptype',
            'rampsize' : '_rampsize',
            'layertype' : '_layertype',
            'layerborder' : '_layerborder',
            'volume' : '_volume',
            'geometry' : None,
            'input' : '_input',
            'vdbtype' : '_vdbtype',
            'forcealign' : '_forcealign',
            'resolution' : '_resolution',
            'voxelsize' : '_voxelsize',
            'xformtoworld' : '_xformtoworld',
            'xformtovoxel' : '_xformtovoxel',
            'attribute' : '_attribute',
            'attribclass' : '_attribclass',
            'attribtype' : '_attribtype',
            'attribsize' : '_attribsize',
            'precision' : '_precision',
            'readable' : '_readable',
            'writeable' : '_writeable',
            'optional' : '_optional',
            'defval' : '_defval',
            'timescale' : '_timescale',
            'intval' : '_intval',
            'fval'   : '_fval',
            'v3val'  : '_v3val',
            'v4val'  : '_v4val',
            }
    elif node.parm('paramcount') is not None:
        # DOP based
        bindparm = 'paramcount'
        bindparmprefix = 'parameter'
        bindparmsuffix = {
            'name' : 'Name',
            'type'   : 'Type',
            'ramp' : 'Ramp',
            'rampsize' : 'RampSize',
            'volume' : 'Volume',
            'geometry' : 'Geometry',
            'input' : None,
            'vdbtype' : None,
            'forcealign' : None,
            'resolution' : 'Resolution',
            'voxelsize' : 'VoxelSize',
            'xformtoworld' : 'XformToWorld',
            'xformtovoxel' : 'XformToVoxel',
            'attribute' : 'Attribute',
            'attribclass' : 'Class',
            'attribtype' : 'AttributeType',
            'attribsize' : 'AttributeSize',
            'precision' : 'Precision',
            'readable' : 'Input',
            'writeable' : 'Output',
            'optional' : 'Optional',
            'defval' : 'DefVal',
            'timescale' : 'TimeScale',
            'intval' : 'Int',
            'fval'   : 'Flt',
            'v3val'  : 'Flt3',
            'v4val'  : 'Flt4',
        }
    else:
        # Unknown
        pass

    # Loop over each binding to see if it exists on explicit bindings,
    # if not add it.
    for binding in bindings:
        # Search our node's bindings...
        numbind = node.parm(bindparm).evalAsInt()
        found = False
        for i in range(1, numbind+1):
            name = node.parm(bindparmprefix + str(i) + bindparmsuffix['name']).evalAsString()
            if name == binding['name']:
                found = True
                break
        if not found:
            requiresparm = False
            tuplesize = 1
            isint = False
            isramp = False
            islayer = False

            # Add to our list if we should have spare parms...
            if binding['type'] in ('int', 'float', 'float3', 'float4'):
                requiresparm = True
                if binding['type'] == 'int':
                    isint = True
                if binding['type'] == 'float3':
                    tuplesize = 3
                if binding['type'] == 'float4':
                    tuplesize = 4
            if binding['type'] in ('attribute', 'volume', 'vdb'):
                # If it is optional and has a defval we want to
                # trigger it
                requiresparm = binding['optional'] and binding['defval']

            # Some cases we don't support...
            if binding['type'] == 'attribute' and (binding['attribtype'] == 'floatarray' or binding['attribtype'] == 'intarray'):
               requiresparm = False

            if binding['type'] == 'attribute' and binding['attribtype'] == 'int':
                isint = True
                if binding['attribsize'] != 1:
                    requiresparm = False
            
            if binding['type'] == 'attribute' and binding['attribtype'] == 'float':
                tuplesize = binding['attribsize']
                if tuplesize not in (1, 3, 4):
                    requiresparm = False
            if binding['type'] == 'ramp':
                isramp = True
                requiresparm = True
                ramptype = hou.rampParmType.Color
                if binding['ramptype'] == 'float':
                    ramptype = hou.rampParmType.Float
            if binding['type'] == 'layer':
                islayer = True
                requiresparm = True

            name = binding['name']
            label = name.title().replace("_", " ")
            # We want to avoid conflict with existing OpenCL parms.
            # we have no need to exactly match as the source isn't a
            # ch("") like it is in VEX.
            internalname = name + '_val'

            if requiresparm:
                if isramp:
                    template = hou.RampParmTemplate(internalname, label, ramptype)
                elif isint:
                    template = hou.IntParmTemplate(internalname, label, tuplesize)
                else:
                    template = hou.FloatParmTemplate(internalname, label, tuplesize, default_value=([1.0]), min=-10, max=10)

                if not islayer:
                    # Check if we have an existing parm.
                    # note the user may have removed an explicit binding,
                    # but left the existing parm, in this case we'll link
                    # to that...
                    exparm = node.parm(internalname) or node.parmTuple(internalname)
                    if not exparm:
                        refs.append((internalname, template))

                # Create our new binding...
                node.parm(bindparm).set(numbind+1)
                numbind += 1

                # Write back our binding values...
                for key in bindparmsuffix:
                    if bindparmsuffix[key] is None:
                        continue
                    if key in ('intval', 'fval', 'v2val', 'v3val', 'v4val', 'v4bval', 'm4val', 'ramp'):
                        continue
                    keyparmname = bindparmprefix + str(numbind) + bindparmsuffix[key]
                    parm = node.parm(keyparmname) or node.parmTuple(keyparmname)
                    if parm: parm.set(binding[key])
                if isramp:
                    ramplinks.append(( internalname, bindparmprefix + str(numbind) + bindparmsuffix['ramp']))
                else:
                    if isint:
                        t = 'intval'
                    elif tuplesize == 3:
                        t = 'v%dval' % tuplesize
                    elif tuplesize == 4:
                        t = 'v%dval' % tuplesize
                    else:
                        t = 'fval'
                    channellinks.append(( internalname,  bindparmprefix + str(numbind) + bindparmsuffix[t], binding[t]))

    # Completed the binding loop, we've extended our bindings to have
    # all the new explicit bindings that we think need parms and build
    # a refs list of them.  channellinks has triples of how we want
    # to then re-link, which we can do after the refs are built.
    _addSpareParmsToStandardFolder(node, parmname, refs)

    for (internalname, srcname, value) in channellinks:
        parm = node.parm(internalname) or node.parmTuple(internalname)
        if parm:
            parm.set(value)
            srcparm = node.parm(srcname) or node.parmTuple(srcname)
            if srcparm: srcparm.set(parm)

    for (internalname, srcname) in ramplinks:
        parm = node.parm(internalname) or node.parmTuple(internalname)
        lin = hou.rampBasis.Linear
        if parm: parm.set(hou.Ramp((lin, lin),(0,1),(0,1)))
        srcparm = node.parm(srcname) or node.parmTuple(srcname)
        # Link the point count
        if srcparm: srcparm.setExpression("ch('" + internalname + "')")
        # Setup opmultiparms
        cmd = 'opmultiparm ' + node.path() + ' "' + srcname + '#pos" "' + internalname + '#pos" "' + srcname + '#value" "' + internalname + '#value" "' + srcname + '#interp" "' + internalname + '#interp"'
        (res, err) = hou.hscript(cmd)

        # Manually link already exisiting parms
        # this should be evalAsInt, but for some reason that is still
        # 1 at this point?
        npt = 2 # parm.evalAsInt()
        for i in range(npt):
            node.parm(srcname + str(i+1) + 'pos').set(node.parm(internalname + str(i+1) + 'pos'))
            node.parm(srcname + str(i+1) + 'value').set(node.parm(internalname + str(i+1) + 'value'))
            node.parm(srcname + str(i+1) + 'interp').set(node.parm(internalname + str(i+1) + 'interp'))

    # no need to dirty an opencl node as we affected cooking parmeters
    # when we updated bindings.

def createSpareParmsFromChCalls(node, parmname):
    """
    For each ch() call in the given parm name, create a corresponding spare
    parameter on the node.
    """

    parm = node.parm(parmname)
    original = parm.unexpandedString()
    simple = True
    if len(parm.keyframes()) > 0:
        # The parm has an expression/keyframes, evaluate it to the get its
        # current value
        code = parm.evalAsString()
        simple = False
    else:
        code = original.strip()
        if len(code) > 2 and code.startswith("`") and code.endswith("`"):
            # The whole string is in backticks, evaluate it
            code = parm.evalAsString()
            simple = False
    # Remove comments
    code = comment_or_string_exp.sub(remove_comments, code)

    # Loop over the channel refs found in the VEX, work out the corresponding
    # template type, remember for later (we might need to check first if the
    # user wants to replace existing parms).
    refs = []
    existing = []
    foundnames = set()
    for match in chcall_exp.finditer(code):
        call = match.group(1)
        name = match.group(2)[1:-1]

        # If the same parm shows up more than once, only track the first
        # case.  This avoids us double-adding since we delay actual
        # creation of parms until we've run over everything.
        if name in foundnames:
            continue
        foundnames.add(name)
        
        size = ch_size.get(call, 1)
        label = name.title().replace("_", " ")

        if call in ("vector(chramp", "vector(chrampderiv"):
            # Result was cast to a vector, assume it's a color
            template = hou.RampParmTemplate(name, label, hou.rampParmType.Color)
        elif call in ("chramp", "chrampderiv"):
            # No explicit cast, assume it's a float
            template = hou.RampParmTemplate(name, label, hou.rampParmType.Float)
        elif call == "chs":
            template = hou.StringParmTemplate(name, label, size)
        elif call == "chsop":
            template = hou.StringParmTemplate(
                name, label, size, string_type=hou.stringParmType.NodeReference)
        elif call == "chi":
            template = hou.IntParmTemplate(name, label, size)
        elif call == "chdict":
            template = hou.DataParmTemplate(
                name, label, size,
                data_parm_type=hou.dataParmType.KeyValueDictionary
            )
        else:
            template = hou.FloatParmTemplate(name, label, size, default_value=([1.0]), min=-10, max=10)

        exparm = node.parm(name) or node.parmTuple(name)
        if exparm:
            if not exparm.isSpare():
                # The existing parameter isn't a spare, so just skip it
                continue
            extemplate = exparm.parmTemplate()
            etype = extemplate.type()
            ttype = template.type()
            if (
                etype != ttype or
                extemplate.numComponents() != template.numComponents() or
                (ttype == hou.parmTemplateType.String and
                 extemplate.stringType() != template.stringType())):
                # The template type is different, remember the name and template
                # type to replace later
                existing.append((name, template))
            else:
                # No difference in template type, we can skip this
                continue
        else:
            # Remember the parameter name and template type to insert later
            refs.append((name, template))

    # If there are existing parms with the same names but different template
    # types, ask the user if they want to replace them
    if existing:
        exnames = ", ".join(f'"{name}"' for name, _ in existing)
        if len(existing) > 1:
            msg = f"Parameters {exnames} already exist, replace them?"
        else:
            msg = f"Parameter {exnames} already exists, replace it?"
        result = hou.ui.displayCustomConfirmation(
            msg, ("Replace", "Skip Existing", "Cancel"), close_choice=2,
            title="Replace Existing Parameters?",
            suppress=hou.confirmType.DeleteSpareParameters,
        )
        if result == 0:  # Replace
            refs.extend(existing)
        elif result == 2:  # Cancel
            return

    # remove spare parms that are not needed anymore
    ptg = node.parmTemplateGroup()
    folder = ptg.findFolder("Generated Channel Parameters")
    if folder:
        parm_templates = folder.parmTemplates()
        for pt in parm_templates:
            if pt.name() not in foundnames:
                try:
                    ptg.remove(pt)
                    node.setParmTemplateGroup(ptg)
                except:
                    print("Error: error removing spare parameter from parm template group")

    _addSpareParmsToStandardFolder(node, parmname, refs)

    if refs:
        if simple:
            # Re-write the contents of the snippet so the node will re-run the
            # VEX and discover the new parameters.
            # (This is really a workaround for a bug (#123616), since Houdini
            # should ideally know to update VEX snippets automatically).
            parm.set(original)


