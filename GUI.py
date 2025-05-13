import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import shutil
import subprocess
import threading
import uuid
from pathlib import Path
import sys

# Папка для временных файлов
TEMP_DIR = Path("temp_files")
TEMP_DIR.mkdir(exist_ok=True)

# Название внешнего скрипта (может отсутствовать)
EXTERNAL_SCRIPT = "external_script.py"


class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработка CSV/XLSX")
        self.root.geometry("420x280")  # Увеличил высоту окна для лучшего отображения
        self.root.resizable(False, False)

        self.filename = None
        self.output_path = None

        # Основной текст
        self.label = ttk.Label(root, text="добавьте файл (csv, xlsx)", font=("Arial", 12))
        self.label.pack(pady=10)

        # Кнопка выбора файла
        self.select_button = ttk.Button(root, text="Выбрать файл", command=self.select_file)
        self.select_button.pack(pady=5)

        # Сообщения (обработка/ошибка/успех)
        self.status_text = tk.StringVar()
        self.status_label = ttk.Label(
            root,
            textvariable=self.status_text,
            font=("Arial", 10),
            wraplength=400,
            foreground="blue",
            justify="center"
        )
        self.status_label.pack(pady=10)

        # Фрейм для кнопок результата
        self.buttons_frame = ttk.Frame(root)
        self.buttons_frame.pack(pady=10)

        # Кнопка "Скачать результат"
        self.download_button = ttk.Button(
            self.buttons_frame,
            text="Скачать результат",
            command=self.download_file
        )

        # Кнопка "Попробовать снова"
        self.retry_button = ttk.Button(
            self.buttons_frame,
            text="Попробовать снова",
            command=self.reset_app
        )

    # Выбор файла
    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV файлы", "*.csv"), ("Excel файлы", "*.xlsx")])
        if not file_path:
            return
        self.filename = file_path
        self.status_text.set("Обработка данных, пожалуйста подождите...")
        self.hide_result_buttons()
        threading.Thread(target=self.process_file, daemon=True).start()

    # Обработка файла
    def process_file(self):
        try:
            # Проверяем наличие внешнего скрипта перед обработкой (.py файл aonokoi)
            if not os.path.exists(EXTERNAL_SCRIPT):
                self.status_text.set("Ошибка: программа не может обработать ваш файл")
                self.show_retry_button()
                return

            unique_id = str(uuid.uuid4())
            extension = Path(self.filename).suffix
            input_path = TEMP_DIR / f"input_{unique_id}{extension}"
            output_path = TEMP_DIR / f"output_{unique_id}{extension}"
            self.output_path = output_path

            shutil.copy(self.filename, input_path)

            # Запуск внешнего скрипта
            command = [sys.executable, EXTERNAL_SCRIPT, str(input_path), str(output_path)]
            result = subprocess.run(command, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                self.status_text.set("Ошибка: " + result.stderr.strip())
                self.show_retry_button()
                return

            self.status_text.set("Спасибо за ожидание!")
            self.show_result_buttons()

        except subprocess.TimeoutExpired:
            self.status_text.set("Ошибка: Время обработки истекло.")
            self.show_retry_button()
        except Exception as e:
            self.status_text.set(f"Ошибка: {str(e)}")
            self.show_retry_button()

    # Показать кнопки результата
    def show_result_buttons(self):
        self.download_button.grid(row=0, column=0, padx=10)
        self.retry_button.grid(row=0, column=1, padx=10)

    # Показать только кнопку повтора
    def show_retry_button(self):
        self.download_button.grid_forget()
        self.retry_button.grid(row=0, column=0, padx=10)

    # Скрыть все кнопки результата
    def hide_result_buttons(self):
        self.download_button.grid_forget()
        self.retry_button.grid_forget()

    # Кнопка "Попробовать снова"
    def reset_app(self):
        self.status_text.set("")
        self.hide_result_buttons()
        self.filename = None
        self.output_path = None

    # Скачивание результата
    def download_file(self):
        if not self.output_path or not os.path.exists(self.output_path):
            messagebox.showerror("Ошибка", "Файл не найден.")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=self.output_path.suffix,
            filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")]
        )
        if save_path:
            try:
                shutil.copy(self.output_path, save_path)
                messagebox.showinfo("Готово", "Файл успешно сохранён.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()