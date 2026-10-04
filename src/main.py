import tkinter as tk
from tkinter import scrolledtext
import shlex

VFS_NAME = "MyVFS"

root = None
out = None
entry = None

def run_command(cmd, args, output, root):
    """Выполняет команду с указанными аргументами.

    Args:
        cmd (str): Имя команды.
        args (list[str]): Список аргументов команды.
        output (Callable[[str], None]): Функция вывода строки
            в окно терминала.
        root (tkinter.Tk): Корневое окно tkinter;
            используется командой exit для закрытия приложения.

    Returns:
        None
    """
    if cmd == "ls":
        output(f"ls: аргументы = {args}")
    elif cmd == "cd":
        output(f"cd: аргументы = {args}")
    elif cmd == "exit":
        root.destroy()
    else:
        output(f"{cmd}: команда не найдена")

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

def on_enter(event):
    """Обрабатывает нажатие клавиши Enter в поле ввода.

    Считывает строку, очищает поле, печатает её в поле вывода,
    разбирает на команду и аргументы с учётом кавычек и передаёт в
    функцию run_command.

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

    try:
        parts = shlex.split(line)
    except ValueError as e:
        print_line(f"ошибка разбора: {e}")
        return

    if not parts:
        return

    cmd, args = parts[0], parts[1:]
    run_command(cmd, args, print_line, root)

def main():
    """Точка входа в программу"""
    global root, out, entry
    root = tk.Tk()
    root.title(VFS_NAME)
    root.geometry("1280x720")

    out = scrolledtext.ScrolledText(root, bg="black", fg="white",
                                    font=("Consolas", 11), state=tk.DISABLED)
    out.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    frame = tk.Frame(root)
    frame.pack(fill=tk.X, padx=5, pady=(0, 5))
    tk.Label(frame, text="$", font=("Consolas", 11)).pack(side=tk.LEFT)
    entry = tk.Entry(frame, font=("Consolas", 11))
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
    entry.focus_set()

    entry.bind("<Return>", on_enter)

    print_line(f"{VFS_NAME}: эмулятор оболочки. Введите команду.")
    print_line()

    root.mainloop()

if __name__ == "__main__":
    main()