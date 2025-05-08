#  面談の予約をWebで行うアプリケーション

## 概要
研究室配属における、面談の予約を行えるアプリケーションです。

運営用ページを作成し、予約の管理や、先生の都合が悪い時間は面談負荷にする等の機能を備えています

![Image](https://github.com/user-attachments/assets/e2630b9b-c004-49bd-865d-58608f0dc8c1)

##　背景
今まで研究室の面談は、希望者が紙に時間を書くことで予約を行っていたが、これは運営側も面接を希望する学生にとっても不便であったため、Web上で予約を行えるようにした。

##  特徴
- Djangoテンプレート言語による、シンプルな記述
- 運営用ページで予約の変更、削除が可能。
- ユーザ認証により、運営用ページへのアクセスを制限
- Bootstrapを用いた、シンプルで見やすいデザイン

## コードの構成
主要なもののみ
- booking/template/booking/*.html __(フロントエンド)__
  - 各機能におけるテンプレートのHTMLファイル。
- booking/static/style.css __(フロントエンド)__
  - ウェブサイトの色やボタンの大きさ等、デザインについての取り決め。
- booking/views.py __(サーバエンド)__
  - 各リクエストを処理し、HTMLを返す。
- booking/models.py __(サーバエンド)__
  - 予約に用いるモデルの定義。

##  使用技術
- Python3 / Django
- Python3 / venv
- Bootstrap
- SQLite

##  実行方法
バージョン

Python 3.10.12

Django 5.0.4

```
cd portfolios/project2_skelton/
Python3 manage.py runserver
```

↑を実行した状態で、ブラウザで http://127.0.0.1:8000 へアクセスしてください。