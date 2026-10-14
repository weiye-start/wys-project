# -*- coding: utf-8 -*-
"""一个命令行待办清单：数据存在 todos.json 里，支持增删改查。

只用标准库 json + argparse。数据文件默认是当前目录的 todos.json，
可以用 --file 换成别的路径。

用法：
    python todo.py add 买牛奶            # 添加一条（可写多个词，会自动拼起来）
    python todo.py list                  # 列出所有条目
    python todo.py done 2                # 把第 2 条标记为完成
    python todo.py rm 2                  # 删除第 2 条
    python todo.py --file D:\\todos.json list   # 指定数据文件

每一条的结构：{"id": 1, "text": "买牛奶", "done": false}
"""
from __future__ import annotations

import argparse
import json
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
    RED = colorama.Fore.RED
    DIM = colorama.Style.DIM
    RESET = colorama.Style.RESET_ALL
except Exception:
    GREEN = CYAN = YELLOW = RED = DIM = RESET = ""


def load_todos(path: Path) -> list[dict]:
    """读取 todos.json。文件不存在就返回空列表。"""
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        print(f"{RED}数据文件损坏，将当作空清单处理：{path}{RESET}")
        return []


def save_todos(todos: list[dict], path: Path) -> None:
    """写回 todos.json。ensure_ascii=False 让中文可读。"""
    path.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")


def next_id(todos: list[dict]) -> int:
    """返回下一个可用序号（已有最大 id + 1）。"""
    return max((t["id"] for t in todos), default=0) + 1


def add_todo(todos: list[dict], text: str) -> list[dict]:
    todo = {"id": next_id(todos), "text": text, "done": False}
    todos.append(todo)
    print(f"{GREEN}已添加 #{todo['id']}：{todo['text']}{RESET}")
    return todos


def list_todos(todos: list[dict]) -> None:
    if not todos:
        print(f"{DIM}清单是空的。用 `python todo.py add 内容` 添加一条吧。{RESET}")
        return
    for t in todos:
        mark = f"{GREEN}[x]{RESET}" if t["done"] else f"{YELLOW}[ ]{RESET}"
        text = f"{DIM}{t['text']}{RESET}" if t["done"] else t["text"]
        print(f"  {t['id']:>3}  {mark}  {text}")
    done = sum(1 for t in todos if t["done"])
    print(f"{CYAN}共 {len(todos)} 条，已完成 {done} 条。{RESET}")


def find_index(todos: list[dict], todo_id: int) -> int | None:
    """按 id 找到下标，找不到返回 None。"""
    for i, t in enumerate(todos):
        if t["id"] == todo_id:
            return i
    return None


def done_todo(todos: list[dict], todo_id: int) -> list[dict]:
    idx = find_index(todos, todo_id)
    if idx is None:
        print(f"{RED}找不到序号 {todo_id}。用 `list` 看一下现有序号。{RESET}")
        return todos
    if todos[idx]["done"]:
        print(f"{YELLOW}#{todo_id} 已经是完成状态。{RESET}")
    else:
        todos[idx]["done"] = True
        print(f"{GREEN}#{todo_id} 已完成：{todos[idx]['text']}{RESET}")
    return todos


def remove_todo(todos: list[dict], todo_id: int) -> list[dict]:
    idx = find_index(todos, todo_id)
    if idx is None:
        print(f"{RED}找不到序号 {todo_id}。{RESET}")
        return todos
    removed = todos.pop(idx)
    print(f"{YELLOW}已删除 #{removed['id']}：{removed['text']}{RESET}")
    return todos


def main() -> int:
    parser = argparse.ArgumentParser(description="命令行待办清单")
    parser.add_argument("--file", type=Path, default=Path("todos.json"), help="数据文件路径")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="添加一条")
    p_add.add_argument("text", nargs="+", help="待办内容")

    sub.add_parser("list", help="列出所有条目")

    p_done = sub.add_parser("done", help="标记完成")
    p_done.add_argument("id", type=int, help="要完成的序号")

    p_rm = sub.add_parser("rm", help="删除一条")
    p_rm.add_argument("id", type=int, help="要删除的序号")

    args = parser.parse_args()
    todos = load_todos(args.file)

    if args.command == "add":
        todos = add_todo(todos, " ".join(args.text))
    elif args.command == "list":
        list_todos(todos)
    elif args.command == "done":
        todos = done_todo(todos, args.id)
    elif args.command == "rm":
        todos = remove_todo(todos, args.id)

    save_todos(todos, args.file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
