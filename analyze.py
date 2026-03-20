"""
analyze.py - output.csv を読み込んで分析するスクリプト

やること:
  1. カテゴリ別の件数をターミナルに表として表示する
  2. カテゴリ別の件数を棒グラフで見せる
  3. グラフを result.png という画像ファイルに保存する
"""

import csv
import sys
from collections import Counter

import matplotlib
import matplotlib.pyplot as plt

# ---- 日本語フォントの設定 ----
# フォントを設定しないとグラフの日本語が「□□□」になってしまう。
# Macに標準で入っている "Hiragino Sans" を優先的に使う。
matplotlib.rcParams["font.family"] = ["Hiragino Sans", "YuGothic", "AppleGothic", "sans-serif"]
# マイナス記号が文字化けしないようにする設定
matplotlib.rcParams["axes.unicode_minus"] = False

# 読み込むファイルと保存するファイルの名前
INPUT_FILE = "output.csv"
OUTPUT_IMAGE = "result.png"

# カテゴリの表示順（この順番で棒グラフに並べる）
CATEGORY_ORDER = ["技術", "ビジネス", "セキュリティ", "法務", "その他"]

# 棒グラフの色（カテゴリごとに色を変える）
BAR_COLORS = {
    "技術": "#4C9BE8",       # 青
    "ビジネス": "#F4A24A",   # オレンジ
    "セキュリティ": "#E85C5C",  # 赤
    "法務": "#6BBF72",       # 緑
    "その他": "#A78FD4",     # 紫
}


def load_csv(filepath: str) -> list[dict]:
    """CSVファイルを読み込んで、行のリストとして返す関数"""
    try:
        with open(filepath, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        # ファイルが見つからないときはエラーを出して終わる
        print(f"エラー: {filepath} が見つかりません。先に classify.py を実行してください。", file=sys.stderr)
        sys.exit(1)
    return rows


def count_by_category(rows: list[dict]) -> dict[str, int]:
    """カテゴリ別に件数を数えて、辞書として返す関数"""
    # Counter を使うと「各値が何回出てきたか」を自動で数えてくれる
    counts = Counter(row["category"] for row in rows)
    return counts


def print_summary_table(counts: dict[str, int], total: int) -> None:
    """カテゴリ別の件数をターミナルに表として表示する関数"""
    print("\n" + "=" * 35)
    print("  カテゴリ別 集計結果")
    print("=" * 35)
    print(f"  {'カテゴリ':<12} {'件数':>4}  {'割合':>6}")
    print("-" * 35)

    for category in CATEGORY_ORDER:
        count = counts.get(category, 0)  # データがないカテゴリは 0 件
        # 割合(%)を計算する。ゼロ割りを防ぐため total が 0 のときは 0 にする
        ratio = (count / total * 100) if total > 0 else 0
        # 棒グラフ風の「■」で視覚的に件数を表す（1件につき ■ 1個）
        bar = "■" * count
        print(f"  {category:<12} {count:>4} 件  {ratio:>5.1f}%  {bar}")

    print("-" * 35)
    print(f"  {'合計':<12} {total:>4} 件  100.0%")
    print("=" * 35 + "\n")


def save_bar_chart(counts: dict[str, int], total: int, output_path: str) -> None:
    """棒グラフを作って画像ファイルとして保存する関数"""

    # グラフに使うカテゴリ名と件数のリストを作る（CATEGORY_ORDER の順番通り）
    labels = CATEGORY_ORDER
    values = [counts.get(cat, 0) for cat in labels]
    colors = [BAR_COLORS[cat] for cat in labels]

    # グラフの大きさを設定（横8インチ × 縦5インチ）
    fig, ax = plt.subplots(figsize=(8, 5))

    # 棒グラフを描く
    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor="white", linewidth=1.2)

    # 各棒の上に件数を表示する
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # 棒の横の中央
            bar.get_height() + 0.05,             # 棒のてっぺんより少し上
            f"{value} 件",
            ha="center",   # 横方向: 中央揃え
            va="bottom",   # 縦方向: 下揃え
            fontsize=11,
            fontweight="bold",
        )

    # グラフのタイトルと軸ラベルを設定する
    ax.set_title(f"ニュース記事カテゴリ分布（全 {total} 件）", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("カテゴリ", fontsize=12)
    ax.set_ylabel("件数", fontsize=12)

    # Y軸の最小値を 0 に固定し、最大値に少し余裕を持たせる
    ax.set_ylim(0, max(values) + 1.5)

    # Y軸の目盛りを整数だけにする（0.5件などが表示されないようにする）
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # 横のグリッド線を薄く表示して見やすくする
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)  # グリッド線を棒の後ろに表示する

    # 上と右の枠線を消してすっきりさせる
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # 余白を自動調整してはみ出しを防ぐ
    plt.tight_layout()

    # 画像として保存する（dpi=150 で印刷にも使えるくらいきれいな解像度）
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()  # メモリを解放する


def main() -> None:
    # --- ステップ1: CSVを読み込む ---
    print(f"{INPUT_FILE} を読み込んでいます...")
    rows = load_csv(INPUT_FILE)
    total = len(rows)
    print(f"  {total} 件のデータを読み込みました。")

    # --- ステップ2: カテゴリ別に件数を数える ---
    counts = count_by_category(rows)

    # --- ステップ3: ターミナルに集計表を表示する ---
    print_summary_table(counts, total)

    # --- ステップ4: 棒グラフを保存する ---
    print(f"グラフを {OUTPUT_IMAGE} に保存しています...")
    save_bar_chart(counts, total, OUTPUT_IMAGE)
    print(f"  保存完了: {OUTPUT_IMAGE}")


if __name__ == "__main__":
    main()
