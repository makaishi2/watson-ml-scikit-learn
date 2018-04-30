# Watson Machine Learning サンプルアプリ

## アプリケーションの説明
このアプリケーションはIBM DSXで機械学習を行い、Watson Machine Learning上に保存、Webサービス化した機械学習モデルをWebサービスによりアクセスし、予測を行うサンプルアプリです。  
機械学習モデルの詳細は[Watson Machine Learning - IBM DSX 上のscikit-learn 機械学習モデルをデプロイする -
](https://qiita.com/makaishi2/items/38371d272d752b6e7647)を参照して下さい。

![](readme_images/wml-sample-1.png)  

## 前提
Watson DSX, Watson MLの導入と、Waton ML上のモデル保存、Webサービス化まで済んでいることを前提とします。  
この手順については、上記リンクに記載されていますが、[Jupyter Notebook](https://github.com/makaishi2/watson-ml-scikit-learn/blob/master/notebook/wml-scikit-learn.ipynb)をダウンロードし、IBM DSX 上にロードして実行すると、短時間でサーバー側準備を行うことも可能です。

## 事前準備
Watson MLのインスタンス名を``machine-learning-1``に変更して下さい。インスタンス名の変更は、サービスの管理画面から行うことが可能です。


## 前提ソフトの導入
次の前提ソフトが導入されていることが前提です。

[gitコマンドラインツール][git]  
[Cloud Foundryコマンドラインツール][cloud_foundry]  
  
注意: Cloud Foundaryのバージョンは最新として下さい。 

## ソースのダウンロード
Githubからアプリケーションのソースをダウンロードします。  
カレントディレクトリのサブディレクトリにソースはダウンロードされるので、あらかじめ適当なサブディレクトリを作り、そこにcdしてから下記のコマンドを実行します。  
ダウンロード後、できたサブディレクトリにcdします。
 

```sh
$ cd (適当なサブディレクトリ)
$ git clone https://github.com/makaishi2/watson-ml-scikit-learn.git
$ cd watson-ml-scikit-learn
```

## CFコマンドでログイン
CFコマンドでbluemix環境にログインします。ログイン名、パスワードはBluemixアカウント登録で登録したものを利用します。  
ログインに成功すると、次のような画面となります。  

```
$ cf api https://api.ng.bluemix.net
$ cf login
```

![](readme_images/cf-login.png)  

## アプリケーションのデプロイ

次のコマンドを実行します。
\<service_name\>はなんでもいいのですが、インターネット上のURLの一部となるので、ユニークな名前を指定します。  
(例) scikit-learn-sample-aka1

```
$ cf push <service_name>
```

## 環境変数の設定

WebサービスのエンドポイントURLに関しては、以下のコマンドで、設定する必要があります。  
(注意) scoring_urlは、Waton Machine Learningの管理ダッシュボードより取得できますが、URLの最後に'/online'を付ける必要がある点に注意して下さい。

```
$ cf set-env <service_name> SCORING_URL <scoring_url>
$ cf restage  <service_name>
```

## アプリケーションのURLと起動

デプロイには数分かかります。デプロイが正常に完了したらアプリケーションを起動できます。  
次のURLをブラウザから指定して下さい。

```
https://<service_name>.mybluemix.net/
```

## アプリケーションを修正する場合

導入手順中、git cloneコマンドでダウンロードしたローカルリポジトリにアプリケーションのソースコードが入っています。アプリケーションを修正したい場合は、ローカルのソースを修正し、再度 "cf push \<service_name\>"コマンドを実行すると、Bluemix上のアプリケーションが更新されます。  

## ローカルで起動する場合

アプリケーションを修正する時は、ローカルでもテストできる方が便利です。そのための手順は以下の通りです。

* Node.jsの導入  
ローカルにNode.jsを導入する必要があります。
[Node.jsダウンロード][node_js]からダウンロードして下さい。
* 認証情報の確認  
BluemixダッシュボードからWMLサービスの管理画面を開き、接続用の認証情報を調べてテキストエディタなどにコピーします。
* .envファイルの設定  
次のコマンドで.env.exampleファイルの雛形から.envをコピーし、エディタで調べたusername, passwordを設定します。

```sh
$ cp .env.example .env
```

```sh
WML_SERVICE_CREDENTIALS_URL=xxxxx
WML_SERVICE_CREDENTIALS_USERNAME=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
WML_SERVICE_CREDENTIALS_PASSWORD=xxxxxxxxxxxx
```

* Node.jsアプリケーションの導入、実行  
以下のコマンドでアプリケーションの導入、実行を行います。

```sh
$ npm install
$ npm start
```

[cloud_foundry]: https://github.com/cloudfoundry/cli#downloads
[git]: https://git-scm.com/downloads
[sign_up]: https://bluemix.net/registration
[node_js]: https://nodejs.org/ja/download/
 
