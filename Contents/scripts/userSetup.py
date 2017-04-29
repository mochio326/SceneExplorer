# # -*- coding: utf-8 -*-

import maya.cmds as cmds


def __register_scnexpl_startup():
    from textwrap import dedent
    cmds.evalDeferred(dedent(
        """
        import scnexpl.startup as s

        s.execute()
        """
    ))


if __name__ == '__main__':
    try:
        print("SceneExplorer startup script has begun")
        __register_scnexpl_startup()
        print("SceneExplorer startup script has finished")

    except Exception as e:
        print("SceneExplorer startup script has ended with error")
        # avoidng the "call userSetup.py chain" accidentally stop,
        # all exception must be collapsed
        import traceback
        traceback.print_exc()
