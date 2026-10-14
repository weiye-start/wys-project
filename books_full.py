# -*- coding: utf-8 -*-
"""抓取 books.toscrape.com 全站图书信息，落成 CSV / JSON 表格。

这是 webspider.py 的升级版：
    1. 修掉原来的 bug：response.coding -> response.encoding = "utf-8"
       （否则价格会打印成 "Â£51.77" 这种乱码）
    2. 拆成函数：get_html / parse_page / scrape_all / save_csv / save_json
    3. 自动翻页：读每页 "li.next a" 的链接，一路抓到最后一页（50 页 / 1000 本）
    4. 每本书取 5 个字段：书名、价格、评分(1-5星)、库存、详情页链接
    5. 稳健性：浏览器 UA 头 + timeout + 失败重试 + 抓完一页 sleep 限速
    6. CSV 用 utf-8-sig 保存，Excel 直接打开不乱码

用法：
    python books_full.py                        # 抓全站（50 页，约 30 秒）
    python books_full.py --max-pages 2          # 只抓前 2 页，快速验证
    python books_full.py --max-pages 3 --json   # 额外导出 JSON
    python books_full.py --out 我的书单.csv --delay 0.5
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

# Windows 控制台默认 GBK，这里改成 UTF-8 输出，避免中文 / £ 报错
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 颜色：优先用 colorama（已安装），失败就退回纯文本
try:
    import colorama

    colorama.init()
    GREEN = colorama.Fore.GREEN
    CYAN = colorama.Fore.CYAN
    YELLOW = colorama.Fore.YELLOW
    RED = colorama.Fore.RED
    RESET = colorama.Style.RESET_ALL
except Exception:  # 环境没有 colorama 时的兜底
    GREEN = CYAN = YELLOW = RED = RESET = ""

BASE_URL = "http://books.toscrape.com/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
FIELDS = ["title", "price", "rating", "availability", "url"]


# --------------------------------------------------------------------------- #
# 抓取 / 解析
# --------------------------------------------------------------------------- #

def get_html(url: str, session: requests.Session, retries: int = 3, timeout: int = 15) -> str:
    """下载网页文本。带重试，并把编码固定成 UTF-8（关键的一行修复）。"""
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=timeout)
            resp.raise_for_status()
            resp.encoding = "utf-8"  # 修复乱码：把 "Â£" 还原成 "£"
            return resp.text
        except requests.RequestException as exc:
            if attempt == retries:
                raise
            wait = 1.0 * attempt
            print(f"{YELLOW}  第 {attempt} 次失败（{exc}），{wait:.0f}s 后重试…{RESET}")
            time.sleep(wait)
    raise RuntimeError("unreachable")


def parse_page(soup: BeautifulSoup, page_url: str) -> list[dict]:
    """解析一页里的所有图书，返回字典列表。"""
    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    books: list[dict] = []

    for article in soup.find_all("article", class_="product_pod"):
        link = article.find("h3").a if article.find("h3") else None

        rating_el = article.find("p", class_="star-rating")
        rating = 0
        if rating_el is not None:
            for cls in rating_el.get("class", []):
                if cls in rating_map:
                    rating = rating_map[cls]
                    break

        avail_el = article.find("p", class_="instock availability")
        availability = avail_el.get_text(" ", strip=True) if avail_el else ""

        price_el = article.find("p", class_="price_color")
        price = price_el.get_text(strip=True) if price_el else ""

        books.append(
            {
                "title": link["title"].strip() if link and link.get("title") else "",
                "price": price,
                "rating": rating,
                "availability": availability,
                "url": urljoin(page_url, link["href"]) if link and link.get("href") else "",
            }
        )
    return books


def scrape_all(max_pages: int | None = None, delay: float = 0.3) -> list[dict]:
    """翻页抓取所有图书。max_pages=None 表示抓完全站。"""
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    url: str | None = BASE_URL
    all_books: list[dict] = []
    page = 0

    while url is not None:
        if max_pages is not None and page >= max_pages:
            break

        html = get_html(url, session)
        soup = BeautifulSoup(html, "html.parser")
        books = parse_page(soup, url)
        all_books.extend(books)
        page += 1

        print(f"{GREEN}  第 {page:>2} 页{RESET}：本页 {len(books):>2} 本，累计 {len(all_books):>4} 本")

        nxt = soup.select_one("li.next a")
        url = urljoin(url, nxt["href"]) if nxt and nxt.get("href") else None

        if url is not None and delay > 0:
            time.sleep(delay)

    return all_books


# --------------------------------------------------------------------------- #
# 落盘
# --------------------------------------------------------------------------- #

def save_csv(books: list[dict], path: Path) -> None:
    """保存为 CSV。utf-8-sig 让 Excel 能正确识别中文/£ 符号。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(books)


def save_json(books: list[dict], path: Path) -> None:
    """保存为 JSON。ensure_ascii=False 保留中文原文。"""
    path.write_text(json.dumps(books, ensure_ascii=False, indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
# 入口
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description="抓取 books.toscrape.com 全站图书 → CSV/JSON")
    parser.add_argument("--max-pages", type=int, default=None, help="最多抓几页（默认抓完所有页）")
    parser.add_argument("--delay", type=float, default=0.3, help="每页之间的间隔秒数（默认 0.3）")
    parser.add_argument("--out", type=Path, default=Path("books.csv"), help="CSV 输出路径")
    parser.add_argument("--json", action="store_true", help="同时导出同名 JSON 文件")
    parser.add_argument("--no-color", action="store_true", help="关闭彩色输出")
    args = parser.parse_args()

    global GREEN, CYAN, YELLOW, RED, RESET
    if args.no_color:
        GREEN = CYAN = YELLOW = RED = RESET = ""

    print(f"{CYAN}开始抓取 {BASE_URL}{RESET}")
    t0 = time.time()
    books = scrape_all(max_pages=args.max_pages, delay=args.delay)
    elapsed = time.time() - t0

    if not books:
        print(f"{RED}没有抓到任何数据，请检查网络。{RESET}")
        return 1

    save_csv(books, args.out)
    print(f"{GREEN}已保存 CSV：{args.out}（{len(books)} 本）{RESET}")

    if args.json:
        json_path = args.out.with_suffix(".json")
        save_json(books, json_path)
        print(f"{GREEN}已保存 JSON：{json_path}{RESET}")

    # 抽查第一本，方便肉眼确认没有乱码
    first = books[0]
    print(
        f"{CYAN}示例：{first['title']} | {first['price']} | {first['rating']} 星 | {first['availability']}{RESET}"
    )
    print(f"{GREEN}完成：共 {len(books)} 本，用时 {elapsed:.1f}s{RESET}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
