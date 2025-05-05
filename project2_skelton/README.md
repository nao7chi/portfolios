#  CS-2のコーディングをサポートする並列スケルトン

## 概要
PythonコードからCS-2上で動作するコードを生成するアプリケーションです。

並列計算をサポートする並列スケルトンという概念をPythonに実装し、容易に並列プログラムを記述できるようにしています。

![Image](https://github.com/user-attachments/assets/cbc6bb7e-39f6-499a-b219-e919bb11c06c)

##　背景
Cerebras CS-2という機械学習を高速化させるために作られたマシンがある。このマシンは画期的なアーキテクチャにより、従来のスパコンにはない強みがあるが、一方でコーディングのハードルが高い。

##  特徴
- 並列スケルトンによる、簡潔なコーディング。
- CS-2の組み込み関数を利用することによる高速化。
- 2次元データにも対応。
- ユーザはPE間通信や状態遷移を意識する必要がない。

## コードの構成
- code-generator __（本体）__
  - コード変換を行う code-generator と生成コードの雛形を持つ code-format から成る。 test.py はテスト用コード。
- skeloton-module
  - Pythonで利用できる並列スケルトン関数群。
- sample-result
  - コード生成の例。 test.py のコードを code-generator の引数に渡して実行すると、残りの4つのコードが生成される。

## 使用技術
- Python3 / ast
- CSL

##  実行方法
Python 3.9 以降であることが必須。

```.\commands.sh```の実行には別途CSLのコンパイラが必要です。
```
pip install skelton-module/
cd code-generator/
Python3 code_generator test.py
./commands.sh
```
