# -*- coding: utf-8 -*-
from textwrap import dedent
import maya.cmds as cmds
import maya.mel as mel

def menu_setup():
    cmd = '''
    buildViewMenu MayaWindow|mainWindowMenu;
    setParent -menu "MayaWindow|mainWindowMenu";
    '''

    mel.eval(cmd)

    cmds.menuItem(divider=True)
    cmds.menuItem(
        'scnexpl_folder',
        label='SceneExplorer',
        subMenu=True,
        tearOff=True
    )

    cmds.menuItem(
        'scnexpl_open',
        label=jpn('open SceneExplorer'),
        annotation="open SceneExplorer",
        parent='scnexpl_folder',
        echoCommand=True,
        command=dedent(
            '''
                import scnexpl.explorer
                scnexpl.explorer.main()
            ''')
    )


def register_runtime_command(opt):

    # check if command already exists, then skip register
    runtime_cmd = dedent('''
        runTimeCommand
            -annotation "{annotation}"
            -category "{category}"
            -commandLanguage "{commandLanguage}"
            -command ({command})
            {cmd_name};
    ''')

    name_cmd = dedent('''
        nameCommand
            -annotation "{annotation}"
            -sourceType "{commandLanguage}"
            -command ("{cmd_name}")
            {cmd_name}NameCommand;
    ''')

    exits = mel.eval('''exists "{}";'''.format(opt['cmd_name']))
    if exits:
        return

    try:
        mel.eval(runtime_cmd.format(**opt))
        mel.eval(name_cmd.format(**opt))

    except Exception as e:
        print opt['cmd_name']
        print opt['command']
        raise e


def register_scnexpl_runtime_command():
    opts = {
        'annotation':      "Open SceneExplorer",
        'category':        "SceneExplorer",
        'commandLanguage': "python",
        'command':         r'''"import scnexpl.explorer as ex\r\ex.main() "''',
        'cmd_name':        "OpenSceneExplorer"
    }
    register_runtime_command(opts)



def jpn(string):
    # type: (str) -> str
    """encode utf8 into cp932"""

    try:
        string = unicode(string, "utf-8")
        string = string.encode("cp932")
        return string

    except Exception:
        return string


def execute():
    menu_setup()
    register_scnexpl_runtime_command()