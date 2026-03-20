"""
classify.py - Anthropic APIを使ってニュース記事タイトルをカテゴリ分類するスクリプト

カテゴリ: 技術 / ビジネス / セキュリティ / 法務 / その他
"""

import csv
import sys
import time
from collections import Counter

import anthropic
from dotenv import load_dotenv

# .envファイルからAPIキーを読み込む
load_dotenv()

# 分類対象のカテゴリ
CATEGORIES = ["技術", "ビジネス", "セキュリティ", "法務", "その他"]

INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"


def classify_title(client: anthropic.Anthropic, title: str) -> str:
    """タイトルをAPIに送りカテゴリを返す"""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=16,
        system=(
            "あなたはニュース記事の分類AIです。"
            "与えられた記事タイトルを以下のカテゴリのいずれか1つに分類してください。\n"
            "カテゴリ: 技術 / ビジネス / セキュリティ / 法務 / その他\n"
            "カテゴリ名のみを出力してください。説明は不要です。"
        ),
        messages=[{"role": "user", "content": title}],
    )

    # レスポンスからカテゴリ名を抽出
    result = response.content[0].text.strip()

    # 既知カテゴリに一致しない場合は「その他」にフォールバック
    for category in CATEGORIES:
        if category in result:
            return category
    return "その他"


def main() -> None:
    # Anthropicクライアントを初期化（ANTHROPIC_API_KEY環境変数から自動取得）
    client = anthropic.Anthropic()

    # input.csvを読み込む
    try:
        with open(INPUT_FILE, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        print(f"エラー: {INPUT_FILE} が見つかりません", file=sys.stderr)
        sys.exit(1)

    results = []
    start_time = time.time()

    for row in rows:
        title = row["title"]
        print(f"分類中: {title}")

        try:
            category = classify_title(client, title)
        except anthropic.AuthenticationError:
            print("エラー: APIキーが無効です。.envのANTHROPIC_API_KEYを確認してください", file=sys.stderr)
            sys.exit(1)
        except anthropic.RateLimitError:
            print("エラー: レート制限に達しました。しばらく待ってから再実行してください", file=sys.stderr)
            sys.exit(1)
        except anthropic.APIError as e:
            print(f"APIエラー: {e}", file=sys.stderr)
            sys.exit(1)

        results.append({"id": row["id"], "title": title, "category": category})
        print(f"  -> {category}")

    elapsed = time.time() - start_time

    # output.csvに結果を書き出す
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "title", "category"])
        writer.writeheader()
        writer.writerows(results)

    # カテゴリ別集計を表示
    counts = Counter(r["category"] for r in results)
    print("\n--- カテゴリ別集計 ---")
    for category in CATEGORIES:
        print(f"  {category}: {counts.get(category, 0)} 件")
    print(f"  合計: {len(results)} 件")

    print(f"\n完了: {OUTPUT_FILE} に {len(results)} 件の結果を保存しました")
    print(f"処理時間: {elapsed:.1f} 秒")


if __name__ == "__main__":
    main()
