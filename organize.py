# -*- coding: utf-8 -*-
"""把文件夹里的文件按扩展名自动归类到子文件夹（图片/文档/视频/音频/压缩包/程序/其他）。

只用 Python 标准库（pathlib + shutil + argparse），不联网、不装新包。

用法：
    python organize.py --source D:\\Downloads              # 整理指定文件夹
    python organize.py --source D:\\Downloads --dry-run    # 先预览，不动任何文件（强烈建议先跑这个）
    python organize.py                                     # 默认整理当前目录

安全说明：
    - 只移动「文件」，不动文件夹
    - 自动跳过隐藏文件（. 开头）和本脚本自身
    - 目标里已有同名文件时，自动加 _1、_2 后缀，绝不覆盖
    - 建议先用 --dry-run 看一遍再实跑
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import colorama

    colorama.init()
    GREEN = colorama.Fore.GREEN
    CYAN = colorama.Fore.CYAN
    YELLOW = colorama.Fore.YELLOW
    RESET = colorama.Style.RESET_ALL
except Exception:
    GREEN = CYAN = YELLOW = RESET = ""

# 扩展名 -> 分类。改成你自己的习惯即可。
CATEGORIES: dict[str, set[str]] = {
    "图片": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".ico"},
    "文档": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv", ".json"},
    "视频": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"},
    "音频": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "程序": {".exe", ".msi", ".bat", ".sh", ".py", ".js", ".jar"},
}


def categorize(suffix: str) -> str:
    """根据扩展名返回分类名，匹配不到就归入「其他」。"""
    suffix = suffix.lower()
    for category, exts in CATEGORIES.items():
        if suffix in exts:
            return category
    return "其他"


def unique_path(target: Path) -> Path:
    """若目标文件已存在，返回一个加 _1/_2 后缀的不重名路径。"""
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    for i in range(1, 10000):
        candidate = target.with_name(f"{stem}_{i}{suffix}")
        if not candidate.exists():
            return candidate
    return target  # 理论上到不了这里


def organize(source: Path, dry_run: bool) -> dict[str, int]:
    """整理 source 目录下的文件，返回每个分类移动了多少个。"""
    files = [p for p in source.iterdir() if p.is_file()]
    moved: dict[str, int] = {}
    self_name = Path(__file__).name

    for file in files:
        # 跳过隐藏文件和脚本自身
        if file.name.startswith(".") or file.name == self_name:
            continue

        category = categorize(file.suffix)
        target_dir = source / category
        target = unique_path(target_dir / file.name)

        # 已经在该分类文件夹里，无需移动
        if file.parent == target_dir:
            continue

        if dry_run:
            print(f"{YELLOW}  [预览]{RESET} {file.name}  ->  {category}\\{target.name}")
        else:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(file), str(target))
            print(f"{GREEN}  [移动]{RESET} {file.name}  ->  {category}\\{target.name}")

        moved[category] = moved.get(category, 0) + 1

    return moved


def main() -> int:
    parser = argparse.ArgumentParser(description="按扩展名整理文件到分类子文件夹")
    parser.add_argument("--source", type=Path, default=Path.cwd(), help="要整理的文件夹（默认当前目录）")
    parser.add_argument("--dry-run", action="store_true", help="只预览不移动")
    parser.add_argument("--no-color", action="store_true", help="关闭彩色输出")
    args = parser.parse_args()

    global GREEN, CYAN, YELLOW, RESET
    if args.no_color:
        GREEN = CYAN = YELLOW = RESET = ""

    source: Path = args.source
    if not source.is_dir():
        print(f"目录不存在：{source}")
        return 1

    mode = "预览（不会移动）" if args.dry_run else "实际整理"
    print(f"{CYAN}整理目录：{source}  [模式：{mode}]{RESET}")

    moved = organize(source, dry_run=args.dry_run)

    print(f"\n{CYAN}汇总：{RESET}")
    if not moved:
        print("  没有需要整理的文件。")
    for category, count in sorted(moved.items(), key=lambda kv: -kv[1]):
        print(f"  {category}：{count} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
