"""
命令行待办事项管理工具

支持五个操作：
  - add     "任务内容"    添加新任务
  - list                  查看所有任务（带编号和状态）
  - done    编号           标记任务为已完成
  - update  编号 "新内容"  修改指定任务
  - delete  编号           删除指定任务

数据持久化存储在 todos.json 文件中。
"""

import json
import os
import sys
from datetime import datetime

# ---- Windows 控制台 UTF-8 编码适配 ----
# Windows 默认使用 GBK 编码的 stdout，无法输出 emoji 等 Unicode 字符。
# 通过将 stdout 重新包装为 UTF-8 编码来解决此问题。
if sys.platform == "win32":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

# 数据存储文件路径
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


def load_todos():
    """从 JSON 文件加载待办事项列表，文件不存在或格式错误时返回空列表。"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        # 文件损坏或不可读时返回空列表，避免程序崩溃
        return []


def save_todos(todos):
    """将待办事项列表保存到 JSON 文件。"""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(todos, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"❌ 错误：无法保存数据 —— {e}")
        return False


def cmd_add(todos, content):
    """添加一条新待办事项。"""
    # 生成新编号：取最大编号 + 1，空列表从 1 开始
    new_id = max([t["id"] for t in todos], default=0) + 1

    task = {
        "id": new_id,
        "content": content,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "done": False,
    }
    todos.append(task)

    if save_todos(todos):
        total = len(todos)
        print(f"✅ 任务 #{new_id} 已添加：{content}")
        print(f"   📊 当前共有 {total} 个待办任务")
    else:
        # 保存失败，回滚内存中的修改
        todos.pop()


def cmd_list(todos):
    """列出所有待办事项。"""
    if not todos:
        print("📭 暂无待办事项，快去添加一个吧！")
        return

    # 按编号排序显示
    todos_sorted = sorted(todos, key=lambda t: t["id"])

    print(f"\n{'─' * 50}")
    print(f"  📋 待办事项列表（共 {len(todos)} 项）")
    print(f"{'─' * 50}")

    for task in todos_sorted:
        status = "✅" if task.get("done") else "⬜"
        created = task.get("created_at", "—")
        print(f"  {status}  #{task['id']:<3}  {task['content']}")
        print(f"         创建于 {created}")

    print(f"{'─' * 50}\n")


def cmd_done(todos, task_id):
    """标记指定编号的任务为已完成。"""
    for task in todos:
        if task["id"] == task_id:
            if task.get("done"):
                print(f"⚠️  任务 #{task_id} 已经是完成状态，无需重复标记")
                return

            task["done"] = True

            if save_todos(todos):
                print(f"🎉 任务 #{task_id} 已标记为完成：{task['content']}")
            else:
                # 保存失败，回滚状态
                task["done"] = False
            return

    # 遍历完未找到该编号
    print(f"❌ 错误：未找到编号为 {task_id} 的任务")


def cmd_update(todos, task_id, new_content):
    """修改指定编号的任务内容。"""
    for task in todos:
        if task["id"] == task_id:
            old_content = task["content"]
            task["content"] = new_content

            if save_todos(todos):
                print(f"✅ 任务 #{task_id} 已更新")
                print(f"   旧内容：{old_content}")
                print(f"   新内容：{new_content}")
            else:
                # 保存失败，回滚修改
                task["content"] = old_content
            return

    # 遍历完未找到该编号
    print(f"❌ 错误：未找到编号为 {task_id} 的任务")


def cmd_delete(todos, task_id):
    """删除指定编号的任务。"""
    for i, task in enumerate(todos):
        if task["id"] == task_id:
            deleted = todos.pop(i)

            if save_todos(todos):
                print(f"✅ 任务 #{task_id} 已删除：{deleted['content']}")
            else:
                # 保存失败，回滚删除操作
                todos.insert(i, deleted)
            return

    # 遍历完未找到该编号
    print(f"❌ 错误：未找到编号为 {task_id} 的任务")


def print_usage():
    """打印使用说明。"""
    print(
        """
📋 命令行待办事项工具 —— 使用说明

  python todo.py add    "任务内容"    添加新任务
  python todo.py list                 查看所有任务
  python todo.py done   <编号>        标记任务已完成
  python todo.py update  <编号> "新内容"  修改任务
  python todo.py delete  <编号>        删除任务

示例：
  python todo.py add    "完成周报"
  python todo.py list
  python todo.py done   1
  python todo.py update 1 "完成周报并提交"
  python todo.py delete 1
    """
    )


def main():
    """主入口：解析命令行参数并分发到对应操作。"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)

    command = sys.argv[1].lower()
    todos = load_todos()

    if command == "add":
        if len(sys.argv) < 3:
            print("❌ 错误：请提供任务内容，例如：python todo.py add \"完成周报\"")
            sys.exit(1)
        cmd_add(todos, sys.argv[2])

    elif command == "list":
        cmd_list(todos)

    elif command == "done":
        if len(sys.argv) < 3:
            print("❌ 错误：请提供任务编号，例如：python todo.py done 1")
            sys.exit(1)
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("❌ 错误：编号必须是一个整数")
            sys.exit(1)
        cmd_done(todos, task_id)

    elif command == "update":
        if len(sys.argv) < 4:
            print("❌ 错误：请提供编号和新内容，例如：python todo.py update 1 \"新内容\"")
            sys.exit(1)
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("❌ 错误：编号必须是一个整数")
            sys.exit(1)
        cmd_update(todos, task_id, sys.argv[3])

    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ 错误：请提供任务编号，例如：python todo.py delete 1")
            sys.exit(1)
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print("❌ 错误：编号必须是一个整数")
            sys.exit(1)
        cmd_delete(todos, task_id)

    else:
        print(f"❌ 错误：未知命令 '{command}'")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
