# SceneExplorer
============

Mayaでシーンファイルを管理する為のエクスプローラです。

![SceneExplorer](/images/sceneexplorer-screenshot-01.png)

ブックマーク機能、履歴、ファイルの絞り込み、読み込み時の自動setProjectなどの機能があります。

##実行方法

ダウロードしたSceneExplorer.pyをスクリプトフォルダ（C:\Users\ユーザー名\Documents\maya\バージョン\ja_JP\scripts）に入れる。

    import SceneExplorer
    SceneExplorer.main()

上記コードをスクリプトエディタ(Python)で実行、もしくはシェルフにコマンドを登録してください。

##使い方

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

##その他

ui/SceneExplorer.ui はQtDesigner用のファイルですが、SceneExplorer.pyからは読み込んでません。
SceneExplorer.py単体で動作する方が使いやすいだろうという事でui→py化して組み込んでます。

##動作確認

動作確認はMAYA2015でのみ行っています。
2014～2016辺りでも使えると思いますが、2017ではPySide2になった影響で多分使えません。

##改訂履歴
* 2017.03.14:
  - バージョン1.00公開