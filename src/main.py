import argparse
import os
import tkinter as tk
from tkinter import scrolledtext, messagebox
import shlex

VFS_NAME = "MyVFS"

root = None
out = None
entry = None

def init_gui(vfs_path, script_path):
    """Создаёт окно, виджеты, запускает скрипт и главный цикл.

    Args:
        vfs_path (str | None): Путь к VFS.
        script_path (str | None): Путь к скрипту.

    Returns:
        None
    """
    global root, out, entry

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
        print_line(f"ls: аргументы = {args}")
        return True
    if cmd == "cd":
        print_line(f"cd: аргументы = {args}")
        return True
    if cmd == "exit":
        root.destroy()
        return True

    print_line(f"{cmd}: команда не найдена")
    return False

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

def main():
    """Точка входа в программу"""
    args = parse_args()
    init_gui(args.vfs, args.script)

if __name__ == "__main__":
    main()