## -*- coding: utf-8 -*-
import sys
import re
import os.path
import subprocess

from PySide import QtCore
from PySide import QtGui
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
from maya import OpenMayaUI as omui
import maya.OpenMaya as om
from shiboken import wrapInstance
import maya.cmds as cmds

import ui.SceneExplorer
reload(ui.SceneExplorer)

class SceneExplorerWeight(MayaQWidgetBaseMixin, QtGui.QDialog, ui.SceneExplorer.Ui_Form):
    TITLE = "SceneExplorer"
    URL = "https://"
    FILTER_DESCRIPTION = ['ALL TYPE', 'MAYA SCENE', 'MAYA ASCII', 'MAYA BINARY', 'FBX', 'OBJ']
    FILTER_EXTENSION = [['*.*'], ['*.ma', '*.mb'], ['*.ma'], ['*.mb'], ['*.fbx'], ['*.obj']]

    def __init__(self, parent=None):
        super(SceneExplorerWeight, self).__init__(parent)
        self.setupUi(self)

        self.dir_model = None
        self.file_model = None
        self.path_history = []
        self.path_history_current = -1
        self.add_path_history_lock = False
        self.bookmark_directory = []
        self.bookmark_file = []

        # オブジェクト名とタイトルの変更
        self.setObjectName(self.TITLE)
        self.setWindowTitle(self.TITLE)

        self.setup_view_directory()
        self.setup_view_file()
        self.setup_view_history()
        self.setup_combo_type()
        self.setup_line_filepath()
        self.setup_line_filter()
        self.setup_view_bookmark()
        self.setup_view_history()

        # コールバック関数の設定
        self.btn_open.clicked.connect(self.callback_open)
        self.btn_option.clicked.connect(self.callback_option)
        self.btn_return.clicked.connect(self.callback_return)
        self.btn_moveon.clicked.connect(self.callback_moveon)
        self.btn_currentproj.clicked.connect(self.callback_currentproj)
        self.radio_history_file.toggled.connect(self.callback_radio_history_change)
        self.radio_bookmark_file.toggled.connect(self.callback_radio_bookmark_change)

        self.set_style_sheet()

    def set_style_sheet(self):
        css = """
        QTreeView {
            alternate-background-color: #3A3A3A;
            background: #333333
        }
        QTreeView::item {
            background-color: transparent;
        }
         QTreeView::item:hover {
            background-color: #415B76;
        }
        QTreeView::item:selected{
             background-color:#678db2;
             bfont: bold;
        }
        """
        self.setStyleSheet(css)

    # -----------------------
    # ui_setup
    # -----------------------
    def setup_view_directory(self, currentpath=None):
        rootpath = ''

        select_path = self.get_view_select(self.view_directory, self.dir_model)
        if select_path == currentpath:
            return
        if currentpath is None:
            currentpath = r'C:/'

        self.dir_model = QtGui.QFileSystemModel()
        self.dir_model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllDirs)
        self.dir_model.setRootPath(rootpath)

        self.view_directory.setModel(self.dir_model)
        self.view_directory.setRootIndex(self.dir_model.index(rootpath))
        self.view_directory.setCurrentIndex(self.dir_model.index(currentpath))
        self.view_directory.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view_directory.header().setVisible(False)
        self.view_directory.hideColumn(3)
        self.view_directory.hideColumn(2)
        self.view_directory.hideColumn(1)
        self.view_directory.setAlternatingRowColors(True);

        # コールバック関数の設定
        # modelをセットし直すとコネクトが解除される？のでここに設置
        dir_sel_model = self.view_directory.selectionModel()
        dir_sel_model.selectionChanged.connect(self.callback_dir_change)

        # QTreeViewにコンテキストを追加
        self.view_directory.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view_directory.customContextMenuRequested.connect(self.directory_context_menu)

    def setup_view_file(self, currentpath=None):
        select_path = self.get_view_select(self.view_file, self.file_model)
        # currentpathが既に選択されているパスの場合は無駄に更新しないように
        if select_path == currentpath:
            return
        if currentpath is None:
            currentpath = select_path

        self.file_model = QtGui.QFileSystemModel()
        self.file_model.setFilter(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Files)
        self.file_model.setRootPath('')

        #フィルターを設定
        file_type = self.combo_type.currentIndex()
        if file_type == -1:
            file_type = 0
        filters = self.FILTER_EXTENSION[file_type]
        if self.line_filter.text() != '':
            tex = self.line_filter.text()
            filters = [re.sub(r'^\*?', tex, f) for f in filters]
        self.file_model.setNameFilters(filters)

        self.view_file.setModel(self.file_model)
        self.view_file.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view_file.setSortingEnabled(True)
        self.view_file.setAlternatingRowColors(True);

        #view_directoryの選択状態に応じてルートパスを設定
        dir_path = self.get_view_select(self.view_directory, self.dir_model)
        self.view_file.setRootIndex(self.file_model.index(dir_path))

        self.view_file.setCurrentIndex(self.file_model.index(currentpath))
        self.repaint()

        # コールバック関数の設定
        # modelをセットし直すとコネクトが解除される？のでここに設置
        file_sel_model = self.view_file.selectionModel()
        file_sel_model.selectionChanged.connect(self.callback_file_change)

        # QTreeViewにコンテキストを追加
        self.view_file.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view_file.customContextMenuRequested.connect(self.file_context_menu)

    def setup_combo_type(self):
        for (des, ex) in zip(self.FILTER_DESCRIPTION, self.FILTER_EXTENSION):
            self.combo_type.addItem("{0}  [{1}]".format(des, ' | '.join(ex)))
        self.combo_type.currentIndexChanged.connect(self.callback_type_change)

    def setup_line_filter(self):
        self.line_filter.returnPressed.connect(self.callback_filter_change)

    def setup_line_filepath(self):
        self.line_filepath.returnPressed.connect(self.callback_filepath_change)

    def setup_view_history(self):
        self.history_model = QtGui.QStandardItemModel()
        list = get_history(self)
        for l in list:
            self.history_model.appendRow(QtGui.QStandardItem(l))

        self.view_history.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view_history.header().setVisible(False)
        self.view_history.setModel(self.history_model)
        self.view_history.setAlternatingRowColors(True);

        his_sel_model = self.view_history.selectionModel()
        his_sel_model.selectionChanged.connect(self.callback_history_change)

        # QTreeViewにコンテキストを追加
        self.view_history.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view_history.customContextMenuRequested.connect(self.history_context_menu)

    def setup_view_bookmark(self):
        self.bookmark_model = QtGui.QStandardItemModel()
        list = get_bookmark(self)
        for l in list:
            self.bookmark_model.appendRow(QtGui.QStandardItem(l))

        self.view_bookmark.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.view_bookmark.header().setVisible(False)
        self.view_bookmark.setModel(self.bookmark_model)
        self.view_bookmark.setAlternatingRowColors(True);

        book_sel_model = self.view_bookmark.selectionModel()
        book_sel_model.selectionChanged.connect(self.callback_bookmark_change)

        # QTreeViewにコンテキストを追加
        self.view_bookmark.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.view_bookmark.customContextMenuRequested.connect(self.bookmark_context_menu)

    # -----------------------
    # ContextMenu
    # -----------------------
    def directory_context_menu(self, pos):
        add_menu_label = ['Add to bookmark']
        action = self.build_context_menu(pos, self.view_directory, self.dir_model, add_menu_label)
        if action == add_menu_label[0]:
            path = self.get_view_select(self.view_directory, self.dir_model)
            add_bookmark('directory', path)
            self.setup_view_bookmark()

    def file_context_menu(self, pos):
        add_menu_label = ['Add to bookmark']
        action = self.build_context_menu(pos, self.view_file, self.file_model, add_menu_label)
        if action == add_menu_label[0]:
            path = self.get_view_select(self.view_file, self.file_model)
            add_bookmark('file', path)
            self.setup_view_bookmark()

    def history_context_menu(self, pos):
        self.build_context_menu(pos, self.view_history, self.history_model)

    def bookmark_context_menu(self, pos):
        add_menu_label = ['Delete']
        action = self.build_context_menu(pos, self.view_bookmark, self.bookmark_model, add_menu_label)
        if action == add_menu_label[0]:
            path = self.get_view_select(self.view_bookmark, self.bookmark_model)
            delete_bookmark(self, path)
            self.setup_view_bookmark()

    def build_context_menu(self, pos, view, model, add_menu_label=None):
        '''
        コンテキストメニューの実行部分。汎用的処理以外は選択項目情報のみ返す
        :param pos: クリック時に渡された位置情報
        :param view: ビューインスタンス
        :param model: モデルインスタンス
        :return:
        '''
        # メニューを作成
        menu = QtGui.QMenu(view)
        menu_labels = ['Show in Explorer']
        if add_menu_label is not None:
            menu_labels.extend(add_menu_label)
        actionlist = []
        for label in menu_labels:
            actionlist.append(menu.addAction(label))
        action = menu.exec_(view.mapToGlobal(pos))
        #menu.close()
        # -----実行部分
        if action is None:
            return None
        text = action.text()
        # Show in Explorer
        if text == menu_labels[0]:
            path = self.get_view_select(view, model)
            # 日本語ファイル対応
            path = path.encode('cp932')
            if os.path.isdir(path):
                subprocess.Popen(r'explorer {0}'.format(path.replace('/', '\\')))
            else:
                subprocess.Popen(r'explorer /select,{0}'.format(path.replace('/', '\\')))
            return None
        return text

    # -----------------------
    # callback
    # -----------------------
    def callback_filepath_change(self):
        file_path = self.line_filepath.text()
        if file_path == '':
            return
        head, tail = os.path.split(file_path)
        name, ex = os.path.splitext(file_path)
        # 拡張子が認識できない場合はパスがフォルダを表している事にする
        if ex == '':
            head = file_path
        self.setup_view_directory(head)
        self.setup_view_file(file_path)
        self.add_path_history()

    def callback_filter_change(self):
        self.setup_view_file()

    def callback_type_change(self):
        self.setup_view_file()

    def callback_dir_change(self, selected, deselected):
        self.view_directory.resizeColumnToContents(0)
        self.setup_view_file()

    def callback_file_change(self, selected, deselected):
        select_path = self.get_view_select(self.view_file, self.file_model)
        old_state = self.line_filepath.blockSignals(True)
        self.line_filepath.setText(select_path)
        self.line_filepath.blockSignals(old_state)
        self.add_path_history()

    def callback_radio_history_change(self):
        self.setup_view_history()

    def callback_radio_bookmark_change(self):
        self.setup_view_bookmark()

    def callback_open(self):
        rtn = scene_open(self.line_filepath.text(), self.chkbox_setproject.isChecked())
        if rtn is not None:
            self.close()

    def callback_option(self):
        open_options()

    def callback_return(self):
        if self.path_history_current == 0:
            return
        self.add_path_history_lock = True
        self.path_history_current -= 1
        file_path = self.path_history[self.path_history_current]
        self.line_filepath.setText(file_path)
        self.callback_filepath_change()
        self.add_path_history_lock = False

    def callback_moveon(self):
        if self.path_history_current == len(self.path_history)-1:
            return
        self.add_path_history_lock = True
        self.path_history_current += 1
        file_path = self.path_history[self.path_history_current]
        self.line_filepath.setText(file_path)
        self.callback_filepath_change()
        self.add_path_history_lock = False

    def callback_history_change(self):
        file_path = self.get_view_select(self.view_history, self.history_model)
        self.line_filepath.setText(file_path)
        self.callback_filepath_change()

    def callback_bookmark_change(self):
        file_path = self.get_view_select(self.view_bookmark, self.bookmark_model)
        self.line_filepath.setText(file_path)
        self.callback_filepath_change()

    def callback_currentproj(self):
        path = get_current_ptoject()
        self.line_filepath.setText(path)
        self.callback_filepath_change()

    # -----------------------
    # Event
    # -----------------------
    def keyPressEvent(self, event):
        event.accept()

    def closeEvent(self, e):
        print('closeEvent')

    # -----------------------
    # Others
    # -----------------------
    def get_view_select(self, view, model):
        '''
        ビューの選択している項目のパスを戻す
        :param view:
        :param model:
        :return:
        '''
        select_model = view.selectionModel()
        # 最初の１回。ビューモデルがセットされる前でアトリビュートが存在していない
        if hasattr(select_model, 'hasSelection') is False:
            return ''
        if select_model.hasSelection() is False:
            return ''
        for index in select_model.selectedIndexes():
            if isinstance(model, QtGui.QFileSystemModel):
                file_path = model.filePath(index)
            if isinstance(model, QtGui.QStandardItemModel):
                file_path = model.data(index)
        return file_path

    def add_path_history(self):
        # 追加がロックされている
        if self.add_path_history_lock is True:
            return
        file_path = self.line_filepath.text()
        if file_path == '':
            return
        # 現在の位置から後ろは情報を削除
        if self.path_history_current != -1:
            if len(self.path_history) > 1:
                del self.path_history[self.path_history_current+1:]

        if len(self.path_history) == 0:
            self.path_history.append(file_path)
        else:
            if self.path_history[-1] != file_path:
                self.path_history.append(file_path)

        self.path_history_current = len(self.path_history) - 1


# #################################################################################################
# ここから実行関数 Maya依存の部分
# #################################################################################################

def get_bookmark_option_var_name(type):
    if type == 'file':
        return 'SceneExplorer_BookmarkFileList'
    elif type == 'directory':
        return 'SceneExplorer_BookmarkDirectoryList'

def get_bookmark(ui):
    '''
    記録されているブックマーク情報を取得する
    :param ui: uiのインスタンス
    :return: フルパスのリスト
    '''
    if ui.radio_bookmark_file.isChecked():
        type = 'file'
    elif ui.radio_bookmark_directory.isChecked():
        type = 'directory'
    option_var_name = get_bookmark_option_var_name(type)
    ls = cmds.optionVar(q=option_var_name)
    if ls == 0:
        ls = []
    return ls

def add_bookmark(type, value):
    '''
    ブックマーク情報を追加する
    :param type: 情報を追加するタイプ
    :param value: 追加するパス
    :return:
    '''
    option_var_name = get_bookmark_option_var_name(type)
    ls = cmds.optionVar(q=option_var_name)
    if ls != 0:
        if value not in ls:
            ls.append(value)
    cmds.optionVar(ca=option_var_name)
    [cmds.optionVar(sva=(option_var_name, i)) for i in ls]
    return

def delete_bookmark(ui, value):
    '''
    ブックマーク情報を削除
    :param type: 情報を追加するタイプ
    :param value: 削除するパス
    :return:
    '''
    if ui.radio_bookmark_file.isChecked():
        type = 'file'
    elif ui.radio_bookmark_directory.isChecked():
        type = 'directory'
    option_var_name = get_bookmark_option_var_name(type)
    ls = cmds.optionVar(q=option_var_name)
    if ls != 0:
        if value in ls:
            ls.remove(value)
    cmds.optionVar(ca=option_var_name)
    [cmds.optionVar(sva=(option_var_name, i)) for i in ls]
    return

def get_history(ui):
    '''
    シーン及びプロジェクトの履歴を取得する
    :param ui: uiのインスタンス
    :return: フルパスのリスト
    '''
    ls = []
    if ui.radio_history_file.isChecked():
        ls = cmds.optionVar(q='RecentFilesList')
    elif ui.radio_history_project.isChecked():
        ls = cmds.optionVar(q='RecentProjectsList')
    return list(reversed(ls))

def open_options():
    '''
    読み込みのオプションの表示
    :return:
    '''
    cmds.OpenSceneOptions()

def get_current_ptoject():
    return cmds.workspace(fn=True)

def get_project_dir(path):
    '''
    mayaプロジェクトのフォルダを探す
    :param path: フォルダまたはファイルパス
    :return: 発見出来ない場合はNone
    '''
    drive = os.path.splitdrive(path)[0]
    parent = os.path.dirname(path)
    if drive+'/' == parent:
        return None
    f = r'{0}/workspace.mel'.format(parent)
    if os.path.isfile(f):
        return parent
    return get_project_dir(parent)

def scene_open(path, set_project):
    '''
    シーンを開く
    :return:
    '''

    def new_open():
        if set_project is True:
            cmds.workspace(project_path, openWorkspace=True)
        io.open(path, file_type, 1)
        add_rectnt_project(project_path)
        add_rectnt_file(path, file_type)

    types = {'.ma': 'mayaAsci', '.mb': 'mayaBinary', '.fbx': 'FBX', '.obj': 'OBJ'}
    if path == '':
        return None
    head, tail = os.path.split(path)
    name, ex = os.path.splitext(path)
    if ex not in types.keys():
        return None
    file_type = types[ex]
    project_path = get_project_dir(path)
    io = om.MFileIO()
    if cmds.file(q=1,sceneName=True) == '':
        new_open()
    else:
        result = cmds.confirmDialog(t='File Open', m='New Scene Open or Import Scene?',
                                    b=['New Scene', 'Import Scene', 'Cancel'],
                                    db='New Scene', cb='Cancel', ds='Cancel')
        if result == 'Cancel':
            return None
        elif result == 'New Scene':
            new_open()
        elif result == 'Import Scene':
            fbx_plugin = 'fbxmaya'
            cmds.loadPlugin('{0:}.mll'.format(fbx_plugin), qt=1)
            if fbx_plugin not in cmds.pluginInfo(q=1, ls=1):
                om.MGlobal.displayError('{0} Plugin in not loaded'.format(fbx_plugin))
                return None
            io.importFile(path, file_type, 1, str(tail.replace('.', '_')))

    # テクスチャのリロード
    #ls = cmds.ls(typ='file', type='mentalrayTexture')
    #[cmds.setAttr(x + '.ftn', cmds.getAttr(x + '.ftn'), type='string') for x in ls]
    return 0

def add_rectnt_project(project):
    '''
    プロジェクトの使用履歴へ記録
    :param project:
    :return:
    '''
    optvar = cmds.optionVar
    opt_list = 'RecentProjectsList'
    ls = optvar(q=opt_list)
    max_size = optvar(q='RecentProjectsMaxSize')
    # 履歴内の同名は削除
    for i, x in enumerate(ls):
        if project == x:
            optvar(rfa=[opt_list, i])
    optvar(sva=[opt_list, project])
    if len(optvar(q=opt_list)) > max_size:
        optvar(rfa=[opt_list, 0])

def add_rectnt_file(file_path, file_type):
    '''
    ファイルの使用履歴へ記録
    :param file_path:
    :param file_type:
    :return:
    '''
    optvar = cmds.optionVar
    opt_list = 'RecentFilesList'
    opt_type = 'RecentFilesTypeList'
    max_size = optvar(q='RecentFilesMaxSize')
    ls = optvar(q=opt_list)
    # 履歴内の同名パスは削除
    for i, x in enumerate(ls):
        if file_path == x:
            optvar(rfa=[opt_list, i])
            optvar(rfa=[opt_type, i])

    optvar(sva=[opt_list, file_path])
    optvar(sva=[opt_type, file_type])
    if len(optvar(q=opt_list)) > max_size:
        optvar(rfa=[opt_list, 0])
        optvar(rfa=[opt_type, 0])

def main():
    # 同名のウインドウが存在したら削除
    ptr = omui.MQtUtil.findWindow(SceneExplorerWeight.TITLE)
    if ptr:
        ui = wrapInstance(long(ptr), QtGui.QWidget)
        ui.deleteLater()
    app = QtGui.QApplication.instance()
    window = SceneExplorerWeight()
    window.show()
    return ui

if __name__ == '__main__':
    main()

#-----------------------------------------------------------------------------
# EOF
#-----------------------------------------------------------------------------