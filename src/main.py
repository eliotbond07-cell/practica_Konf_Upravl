import argparse
import os
import copy
import json
import time
import shlex
import tkinter as tk
from tkinter import scrolledtext, messagebox

VFS_NAME = "MyVFS"
DEFAULT_VFS = {"type": "dir", "name": "/", "children": []}
error_vfs = False

root = None
out = None
entry = None

vfs = None
vfs_path = None
vfs_original = None
cwd = []
start_time = None

def init_gui(vfs_path_arg, script_path):
    """Создаёт окно, виджеты, запускает скрипт и главный цикл.

    Args:
        vfs_path_arg (str | None): Путь к VFS.
        script_path (str | None): Путь к скрипту.

    Returns:
        None
    """
    global root, out, entry, vfs, vfs_path, vfs_original, cwd, start_time
    vfs_path = vfs_path_arg
    cwd = []
    start_time = time.time()

    root = tk.Tk()
    title = os.path.basename(vfs_path) if vfs_path else "default"
    root.title(f"{VFS_NAME} - {title}")
    root.geometry("1280x720")

    out = scrolledtext.ScrolledText(
        root, bg="black", fg="white",
        font=("Consolas", 11), state=tk.DISABLED,
    )
    out.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=5, pady=(0, 5))
    tk.Label(frame, text="$", font=("Consolas", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(frame, font=("Consolas", 11))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    entry.focus_set()
    entry.bind("<Return>", on_enter)

    debug_config(vfs_path, script_path)
    vfs = load_vfs(vfs_path)
    vfs_original = copy.deepcopy(vfs)
    if not error_vfs:
        print_line(f"VFS загружена: {vfs_path or 'default'}\n")
        print_line(f"Корень содержит узлов: "
                   f"{len(vfs.get('children', []))}\n")
    if script_path:
        run_script(script_path)
    else:
        print_line(f"{VFS_NAME}: эмулятор оболочки. Введите команду.")
        print_line()

    root.mainloop()

def parse_args(argv=None):
    """Разбирает параметры командной строки.

    Args:
        argv (list[str] | None): Аргументы. None - взять sys.argv[1:].

    Returns:
        argparse.Namespace: С полями vfs и script.
    """
    parser = argparse.ArgumentParser(
        prog="emulator",
        description=f"Эмулятор оболочки (VFS: {VFS_NAME})",
    )
    parser.add_argument("--vfs", default=None,
                        help="Путь к физическому расположению VFS.")
    parser.add_argument("--script", default=None,
                        help="Путь к стартовому скрипту.")
    return parser.parse_args(argv)

def parse(line):
    """Разбирает строку на команду и аргументы с учётом кавычек.

    Args:
        line (str): Строка ввода.

    Returns:
        tuple[str, list[str]] | None: (команда, аргументы) или None
        при ошибке разбора.
    """
    try:
        parts = shlex.split(line)
    except ValueError as e:
        print_line(f"parse error: {e}")
        return None
    if not parts:
        return None
    return parts[0], parts[1:]

def run_command(cmd, args):
    """Выполняет команду с указанными аргументами.

    Args:
        cmd (str): Имя команды.
        args (list[str]): Список аргументов команды.

    Returns:
        bool: True при успехе, False при неизвестной команде.
    """
    if cmd == "ls":
        return cmd_ls()
    if cmd == "cd":
        return cmd_cd(args)
    if cmd == "uptime":
        return cmd_uptime()
    if cmd == "uname":
        return cmd_uname()
    if cmd == "vfs-init":
        return cmd_vfs_init()
    if cmd == "exit":
        return cmd_exit()

    print_line(f"{cmd}: команда не найдена")
    return False

def cmd_ls():
    """Показывает содержимое текущей папки.

    Returns:
        bool: True при успехе.
    """
    node = get_node(cwd)
    if node is None or node.get("type") != "dir":
        print_line("ls: текущая папка недоступна")
        return False

    children = node.get("children", [])
    if not children:
        print_line("(пусто)")
        return True

    for child in children:
        prefix = "d " if child["type"] == "dir" else "- "
        print_line(prefix + child["name"])
    return True

def cmd_cd(args):
    """Переходит в другую папку.

    Поддерживает: без аргументов (в корень), '/', '..', имя папки.

    Args:
        args (list[str]): Аргументы: 0 или 1 путь.

    Returns:
        bool: True при успехе.
    """
    global cwd

    if len(args) > 1:
        print_line("cd: слишком много аргументов")
        return False

    if not args or args[0] == "/":
        cwd = []
        return True

    target = args[0]
    if target == "..":
        if cwd:
            cwd = cwd[:-1]
        return True

    node = get_node(cwd)
    if node is None:
        print_line("cd: текущая папка недоступна")
        return False

    for child in node.get("children", []):
        if child["name"] == target and child["type"] == "dir":
            cwd = cwd + [target]
            return True

    print_line(f"cd: нет такой папки: {target}")
    return False

def cmd_uptime():
    """Показывает время работы эмулятора."""
    if start_time is None:
        print_line("uptime: эмулятор ещё не запущен")
        return False

    seconds = int(time.time() - start_time)
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    print_line(f"up {hours:02d}:{minutes:02d}:{secs:02d}")
    return True

def cmd_uname():
    """Показывает информацию о системе."""
    print_line(f"{VFS_NAME} emulator 1.0 (Python VFS)")
    return True

def cmd_vfs_init():
    """Сбрасывает VFS к состоянию по умолчанию.

    Заменяет текущую VFS на VFS по умолчанию и очищает физический
    файл, если он был задан.

    Returns:
        bool: True при успехе.
    """
    global vfs, vfs_original, cwd

    vfs = copy.deepcopy(DEFAULT_VFS)
    vfs_original = copy.deepcopy(DEFAULT_VFS)
    cwd = []

    if vfs_path:
        try:
            with open(vfs_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_VFS, f)
            print_line(f"vfs-init: VFS сброшена, файл очищен: {vfs_path}")
        except OSError as e:
            print_line(f"vfs-init: не удалось очистить файл: {e}")
            return False
    else:
        print_line("vfs-init: VFS сброшена к default")

    return True

def cmd_exit():
    """Выполняет команду exit."""
    root.destroy()
    return True

def execute(line):
    """Разбирает и выполняет строку.

    Args:
        line (str): Строка команды.

    Returns:
        bool: True при успехе, False при ошибке.
    """
    parsed = parse(line)
    if parsed is None:
        return False
    cmd, args = parsed
    return run_command(cmd, args)

def run_script(path):
    """Выполняет стартовый скрипт с остановкой на первой ошибке.

    Args:
        path (str): Путь к файлу скрипта.

    Returns:
        None
    """
    print_line(f"=== выполнение скрипта: {path} === \n")

    if not os.path.isfile(path):
        fail_script(f"Скрипт не найден: {path}")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as e:
        fail_script(f"Не удалось прочитать скрипт: {e}")
        return

    for i, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        print_line(f"$ {line}")
        if not execute(line):
            fail_script(f"Ошибка на строке {i}: {line!r}")
            return

    print_line("\n=== скрипт завершён успешно ===")
    print_line(f"{VFS_NAME}: интерактивный режим. Введите команду.\n")

def fail_script(msg):
    """Сообщает об ошибке в скрипте и останавливает его.

    Args:
        msg (str): Текст ошибки.

    Returns:
        None
    """
    full = msg + "\nВыполнение остановлено."
    print_line(f"\nERROR: {full}")
    messagebox.showerror("Ошибка скрипта", full)

def print_line(text=""):
    """Печатает строку в область вывода терминала.

    Args:
        text (str, optional): Текст для вывода. По умолчанию пустая строка.

    Returns:
        None
    """
    out.config(state=tk.NORMAL)
    out.insert(tk.END, text + "\n")
    out.see(tk.END)
    out.config(state=tk.DISABLED)

def debug_config(vfs_path, script_path):
    """Печатает отладочную информацию о параметрах запуска.

    Args:
        vfs_path (str | None): Путь к VFS.
        script_path (str | None): Путь к скрипту.

    Returns:
        None
    """
    print_line("======= debug: parameters =======")
    print_line(f"  VFS name    : {VFS_NAME}")
    print_line(f"  VFS path    : {vfs_path or '<not set>'}")
    print_line(f"  script path : {script_path or '<not set>'}")
    print_line("=================================\n")

def on_enter(event):
    """Обрабатывает нажатие клавиши Enter в поле ввода.

    Args:
        event (tkinter.Event): Событие tkinter. Не используется.

    Returns:
        None
    """
    line = entry.get()
    entry.delete(0, tk.END)
    print_line(f"$ {line}")
    if not line.strip():
        return
    execute(line)

def load_vfs(path):
    """Загружает VFS из JSON-файла.

    Args:
        path (str | None): Путь к файлу. None - VFS по умолчанию.

    Returns:
        dict: Корневой узел VFS.
    """
    global error_vfs
    error_vfs = False

    if not path:
        return copy.deepcopy(DEFAULT_VFS)
    if not os.path.isfile(path):
        print_line(f"VFS не найден: {path}, берём default\n")
        error_vfs = True
        return copy.deepcopy(DEFAULT_VFS)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print_line(f"Ошибка загрузки VFS: {e}")
        return copy.deepcopy(DEFAULT_VFS)

def get_node(path_parts):
    """Возвращает узел VFS по списку имён от корня.

    Args:
        path_parts (list[str]): Путь по именам ([] - корень).

    Returns:
        dict | None: Узел или None, если не найден.
    """
    node = vfs
    for name in path_parts:
        if node.get("type") != "dir":
            return None
        found = None
        for child in node.get("children", []):
            if child["name"] == name:
                found = child
                break
        if found is None:
            return None
        node = found
    return node

def main():
    """Точка входа в программу"""
    args = parse_args()
    init_gui(args.vfs, args.script)

if __name__ == "__main__":
    main()