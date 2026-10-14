# -*- coding: utf-8 -*-
"""一个命令行番茄钟：倒计时 + 彩色进度条 + 结束响铃 + 专注统计。

只用标准库 time/json/argparse，配 ANSI 彩色（和你 wy.c / run.py 里一样的
\\033[32m 那套写法）。统计存在 pomo_stats.json 里。

用法：
    python pomo.py                # 默认 25 分钟
    python pomo.py --minutes 5    # 快速试 5 分钟
    python pomo.py --report       # 只看累计统计，不启动计时
    python pomo.py --no-color     # 关闭彩色（管道/日志用）

倒计时中按 Ctrl+C 可随时提前退出，不会报错。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ANSI 颜色（和 test.py / run.py 里的写法一致）
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

STATS_FILE = Path("pomo_stats.json")

HEART = r"""
  ***   ***
 ***** *****
***********
 *********
  *******
   *****
    ***
     *
"""


def fmt_time(seconds: int) -> str:
    """把秒数格式化成 mm:ss。"""
    mm, ss = divmod(seconds, 60)
    return f"{mm:02d}:{ss:02d}"


def render(remaining: int, total: int) -> None:
    """用回车覆盖同一行，画出倒计时 + 进度条。"""
    width = 30
    elapsed = total - remaining
    filled = round(elapsed / total * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = elapsed / total * 100
    line = f"\r{YELLOW}[番茄钟]{RESET} 剩余 {CYAN}{fmt_time(remaining)}{RESET}  [{bar}] {pct:3.0f}%"
    sys.stdout.write(line)
    sys.stdout.flush()


def beep() -> None:
    """结束提示音：先试 \\a，Windows 下再用 winsound 补一记。"""
    print("\a", end="", flush=True)
    try:
        import winsound

        winsound.Beep(880, 400)
        winsound.Beep(660, 400)
    except Exception:
        pass


def load_stats() -> dict:
    """读取统计。文件不存在返回空统计。"""
    if not STATS_FILE.is_file():
        return {"sessions": 0, "minutes": 0}
    try:
        data = json.loads(STATS_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"sessions": 0, "minutes": 0}
    except (json.JSONDecodeError, OSError):
        return {"sessions": 0, "minutes": 0}


def save_stats(stats: dict) -> None:
    STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def run_timer(minutes: int) -> None:
    total = minutes * 60
    remaining = total
    print(f"{GREEN}开始 {minutes} 分钟专注…（Ctrl+C 随时退出）{RESET}")
    try:
        while remaining > 0:
            render(remaining, total)
            time.sleep(1)
            remaining -= 1

        render(0, total)
        print()  # 结束换行
        print(f"{GREEN}时间到！干得漂亮 🎉{RESET}")
        print(CYAN + HEART + RESET)
        beep()

        stats = load_stats()
        stats["sessions"] += 1
        stats["minutes"] += minutes
        save_stats(stats)
        print(f"{CYAN}累计：{stats['sessions']} 次专注，共 {stats['minutes']} 分钟。{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}已提前退出（还剩 {fmt_time(remaining)}）。本次不计入统计。{RESET}")


def show_report() -> None:
    stats = load_stats()
    if stats["sessions"] == 0:
        print("还没有完成过任何一次专注。")
        return
    print(f"{CYAN}累计完成 {stats['sessions']} 次专注，共 {stats['minutes']} 分钟。{RESET}")


def main() -> int:
    parser = argparse.ArgumentParser(description="命令行番茄钟")
    parser.add_argument("--minutes", type=int, default=25, help="专注时长（分钟，默认 25）")
    parser.add_argument("--report", action="store_true", help="只看累计统计")
    parser.add_argument("--no-color", action="store_true", help="关闭彩色输出")
    args = parser.parse_args()

    global GREEN, CYAN, YELLOW, RED, RESET
    if args.no_color:
        GREEN = CYAN = YELLOW = RED = RESET = ""

    if args.minutes <= 0:
        print(f"{RED}时长必须是正数。{RESET}")
        return 1

    if args.report:
        show_report()
    else:
        run_timer(args.minutes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
