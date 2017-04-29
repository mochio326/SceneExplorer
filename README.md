# SceneExplorer [Var.1.1.0]


Mayaでシーンファイルを管理する為のエクスプローラです。

![SceneExplorer](/images/sceneexplorer-screenshot-01.png)

ブックマーク機能、履歴、ファイルの絞り込み、読み込み時の自動setProjectなどの機能があります。

## インストール

1. Clone or download > Download ZIP からZIPファイルをダウンロードしてください。

2. 解凍したSceneExplorerフォルダを `C:\Program Files\Autodesk\ApplicationPlugins` へコピーしてください。  
MayaをCドライブ以外にインストールしている場合でもSceneExplorerフォルダは `C:\Program Files\Autodesk\ApplicationPlugins` に置く必要があるようです。  
判断に迷ったらボーナスツールと同じ場所に入れて下さい。


+ ApplicationPluginsフォルダが存在しない場合は作成してください。

+ 複数バージョンのMayaに対応しています。2015以降のバージョンでは自動的に認識されツールが使える状態になります。

+ 不要になった場合はフォルダを削除してください。

+ バージョンアップの際は上書きではなく、一度SceneExplorerフォルダを削除すると安全です。

## 実行

メインメニュー > Windows > SceneExplorer から開くことが可能です。  
もしくは Hotkey Editor > Custom Scripts > SceneExplorer からホットキーを割り振ることもできます。  


## 使い方

![SceneExplorer](/images/sceneexplorer-screenshot-02.png)

画面上部の左がフォルダービュー、右がファイルビューになります。
その下のテキストボックスが現在選択されているファイルパスになります。

ファイルパスに表示されているパスをOpenボタンで開きます。
既にシーンが開かれている場合は、シーンを新しくするか、インポートするかを選べます。

入力履歴の進む、戻るボタンや各種フィルタも使えます。
詳しくは下のGIFをどうぞ

![SceneExplorer](/images/sceneexplorer-screenshot-03.gif)

各ビューを右クリックすることでブックマークの登録、削除が行えます。
また、Show in Explorerを選択すると選択パスをファイルエクスプローラで開くことができます。

![SceneExplorer](/images/sceneexplorer-screenshot-04.gif)

## 動作確認

MAYA2015：問題なし

MAYA2016：問題なし

MAYA2017：問題なし


## 改訂履歴

2017/4/30
+ バージョン1.1.0
+ PackageContents.xml形式に対応。
+ MAYA2016/MAYA2017に対応

2017/03/15
+ パス指定時にフォルダツリーがアクティブな行に自動スクロールすように対応
  
2017/03/14
+ バージョン1.00公開