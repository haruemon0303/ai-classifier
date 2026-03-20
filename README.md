# ai-classifier

Anthropic の Claude API を使って、ニュース記事のタイトルをカテゴリに自動分類し、結果をグラフ化するツールです。

## 概要

```
input.csv（記事タイトル一覧）
    ↓ classify.py（Claude API で分類）
output.csv（カテゴリ付き結果）
    ↓ analyze.py（集計・グラフ化）
result.png（棒グラフ画像）
```

### 分類カテゴリ

| カテゴリ | 例 |
|--------|-----|
| 技術 | 新モデル発表、自動運転AI開発 |
| ビジネス | 投資・提携・料金改定 |
| セキュリティ | サイバー攻撃、情報漏洩 |
| 法務 | 著作権訴訟、規制法案 |
| その他 | 上記に当てはまらないもの |

## ファイル構成

```
ai-classifier/
├── classify.py   # 記事タイトルを Claude API で分類する
├── analyze.py    # 分類結果を集計・グラフ化する
├── input.csv     # 分類したい記事タイトルの入力ファイル
├── output.csv    # 分類結果（classify.py が生成）
├── result.png    # 棒グラフ画像（analyze.py が生成）
└── .env          # APIキーの設定ファイル（自分で作成）
```

## 必要な環境

- Python 3.11 以上
- Anthropic API キー（[Anthropic Console](https://console.anthropic.com/) で取得）

## セットアップ

### 1. 仮想環境を作成して有効化

```bash
python3 -m venv .venv
source .venv/bin/activate   # Mac / Linux
# .venv\Scripts\activate   # Windows の場合
```

### 2. 必要なパッケージをインストール

```bash
pip install anthropic python-dotenv matplotlib
```

### 3. APIキーを設定

プロジェクトのルートに `.env` ファイルを作成し、APIキーを記述します。

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
```

> `.env` はGitに含めないよう `.gitignore` に追加してください。

## 実行方法

### ステップ1: 記事タイトルを分類する

```bash
python classify.py
```

`input.csv` の各タイトルを Claude API に送り、カテゴリを判定して `output.csv` に保存します。

**実行例:**
```
分類中: OpenAIが新モデル「GPT-5」を発表、推論能力が大幅に向上
  -> 技術
分類中: ソフトバンクがAIスタートアップへ1000億円規模の追加投資を発表
  -> ビジネス
...
--- カテゴリ別集計 ---
  技術: 2 件
  ビジネス: 2 件
  セキュリティ: 2 件
  法務: 2 件
  その他: 2 件
  合計: 10 件

完了: output.csv に 10 件の結果を保存しました
処理時間: 12.3 秒
```

### ステップ2: 結果を分析・グラフ化する

```bash
python analyze.py
```

`output.csv` を読み込み、ターミナルに集計表を表示しつつ `result.png` にグラフを保存します。

**実行例:**
```
===================================
  カテゴリ別 集計結果
===================================
  カテゴリ           件数      割合
-----------------------------------
  技術              2 件   20.0%  ■■
  ビジネス            2 件   20.0%  ■■
  セキュリティ          2 件   20.0%  ■■
  法務              2 件   20.0%  ■■
  その他             2 件   20.0%  ■■
-----------------------------------
  合計             10 件  100.0%
===================================

グラフを result.png に保存しています...
  保存完了: result.png
```

## input.csv のフォーマット

1行目はヘッダー（`id,title`）、2行目以降に記事を追加します。

```csv
id,title
1,OpenAIが新モデル「GPT-5」を発表、推論能力が大幅に向上
2,生成AIの著作権問題で国内初の訴訟、クリエイター団体が大手IT企業を提訴
```

## エラーが出たときは

| エラーメッセージ | 対処法 |
|--------------|--------|
| `APIキーが無効です` | `.env` の `ANTHROPIC_API_KEY` を確認 |
| `input.csv が見つかりません` | `input.csv` がプロジェクトフォルダにあるか確認 |
| `output.csv が見つかりません` | `classify.py` を先に実行する |
| `レート制限に達しました` | しばらく待ってから再実行する |
