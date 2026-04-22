import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu
from .controller import CalculatorController
from .processor import TOperation

class CalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Универсальный калькулятор")
        self.root.resizable(False, False)

        self.controller = CalculatorController(mode="PNumber", base=10, precision=6, real_mode=True)

        self.display_var = tk.StringVar()
        self.memory_var = tk.StringVar(value=" ")
        self.base_var = tk.StringVar(value="10")
        self.mode_var = tk.StringVar(value="p-ичные числа")

        self.create_menu()
        self.create_widgets()
        self.update_display()

        self.root.bind('<Key>', self.on_keypress)

    def create_menu(self):
        menubar = Menu(self.root)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)

        edit_menu = Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Копировать", command=self.copy_to_clipboard, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste_from_clipboard, accelerator="Ctrl+V")
        menubar.add_cascade(label="Правка", menu=edit_menu)
        self.root.bind_all("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind_all("<Control-v>", lambda e: self.paste_from_clipboard())

        mode_menu = Menu(menubar, tearoff=0)
        mode_menu.add_command(label="p-ичные числа", command=lambda: self.switch_mode("PNumber"))
        mode_menu.add_command(label="Простые дроби", command=lambda: self.switch_mode("TFrac"))
        mode_menu.add_command(label="Комплексные числа", command=lambda: self.switch_mode("TComplex"))
        menubar.add_cascade(label="Режим", menu=mode_menu)

        settings_menu = Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Основание системы...", command=self.dialog_base)
        settings_menu.add_command(label="Точность...", command=self.dialog_precision)
        settings_menu.add_separator()
        self.real_mode_var = tk.BooleanVar(value=True)
        settings_menu.add_checkbutton(label="Целые числа (только для p-ичных)", variable=self.real_mode_var,
                                      command=self.toggle_real_mode)
        menubar.add_cascade(label="Настройка", menu=settings_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)

        history_menu = Menu(menubar, tearoff=0)
        history_menu.add_command(label="Показать историю", command=self.show_history)
        menubar.add_cascade(label="История", menu=history_menu)

        self.root.config(menu=menubar)

    def create_widgets(self):
        # Верхняя панель: метка режима, память, дисплей
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=5, fill=tk.X)

        self.mode_label = tk.Label(top_frame, textvariable=self.mode_var, font=("Arial", 10), width=18, anchor="w")
        self.mode_label.pack(side=tk.LEFT)

        self.mem_label = tk.Label(top_frame, textvariable=self.memory_var, font=("Arial", 12), width=3)
        self.mem_label.pack(side=tk.LEFT)

        self.display = tk.Entry(top_frame, textvariable=self.display_var, font=("Arial", 18), justify="right", state='readonly')
        self.display.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Метка для отображения текущего выражения
        self.expr_label = tk.Label(self.root, text="", font=("Arial", 10), anchor="e", fg="gray")
        self.expr_label.pack(fill=tk.X, padx=5)

        # Панель основания (только для p-ичных и комплексных)
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=5, fill=tk.X)
        self.base_label = tk.Label(control_frame, text="Основание:")
        self.base_label.pack(side=tk.LEFT)
        self.base_spin = tk.Spinbox(control_frame, from_=2, to=16, width=3, command=self.change_base_spin,
                                    textvariable=self.base_var)
        self.base_spin.pack(side=tk.LEFT, padx=5)
        self.update_base_visibility()

        # Кнопки
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=5)

        static_buttons = [
            ('MC', 0, 0), ('MR', 0, 1), ('MS', 0, 2), ('M+', 0, 3), ('C', 0, 4), ('CE', 0, 5),
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3), ('*', 1, 4), ('⌫', 1, 5),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('-', 2, 3), ('+', 2, 4), ('=', 2, 5),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('Sqr', 3, 3), ('Rev', 3, 4), ('√', 3, 5),
            ('0', 4, 0), ('.', 4, 1), ('±', 4, 2), ('i', 4, 3)
        ]

        for text, row, col in static_buttons:
            btn = tk.Button(self.buttons_frame, text=text, width=5,
                            command=lambda t=text: self.on_button(t))
            btn.grid(row=row, column=col, padx=2, pady=2)
            if text == '.':
                self.dot_button = btn
            if text == 'i':
                self.i_button = btn

        # Кнопки A-F
        self.hex_buttons = []
        for i, ch in enumerate('ABCDEF'):
            row = 5 + i // 3
            col = i % 3
            btn = tk.Button(self.buttons_frame, text=ch, width=5,
                            command=lambda d=ch: self.on_button(d))
            btn.grid(row=row, column=col, padx=2, pady=2)
            self.hex_buttons.append(btn)

        self.update_ui_for_mode()

    def update_base_visibility(self):
        if self.controller.mode in ("PNumber", "TComplex"):
            self.base_label.pack(side=tk.LEFT)
            self.base_spin.pack(side=tk.LEFT, padx=5)
        else:
            self.base_label.pack_forget()
            self.base_spin.pack_forget()

    def update_ui_for_mode(self):
        mode = self.controller.mode
        if mode == "PNumber":
            self.mode_var.set("p-ичные числа")
        elif mode == "TFrac":
            self.mode_var.set("простые дроби")
        else:
            self.mode_var.set("комплексные числа")

        self.update_base_visibility()

        # Кнопка i
        if mode == "TComplex":
            self.i_button.config(state=tk.NORMAL)
        else:
            self.i_button.config(state=tk.DISABLED)

        # Кнопки A-F
        base = self.controller.base
        needed = [chr(ord('A')+i) for i in range(max(0, base-10))] if mode in ("PNumber", "TComplex") else []
        for i, btn in enumerate(self.hex_buttons):
            if i < len(needed):
                btn.config(state=tk.NORMAL)
                btn.grid()
            else:
                btn.config(state=tk.DISABLED)
                btn.grid_remove()

        # Точка
        if mode == "PNumber" and self.controller.real_mode:
            self.dot_button.config(state=tk.NORMAL)
        else:
            self.dot_button.config(state=tk.DISABLED)

    def update_display(self):
        self.display_var.set(self.controller.get_display_string())
        self.memory_var.set(self.controller.memory.state_string())
        self.base_var.set(str(self.controller.base))
        self.expr_label.config(text=self.controller.get_expression())
        self.update_ui_for_mode()

    def switch_mode(self, mode):
        self.controller.switch_mode(mode)
        self.update_display()

    def change_base_spin(self):
        try:
            new_base = int(self.base_var.get())
            if 2 <= new_base <= 16:
                self.controller.set_base(new_base)
                self.update_display()
            else:
                self.base_var.set(str(self.controller.base))
        except:
            self.base_var.set(str(self.controller.base))

    def dialog_base(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Основание системы")
        tk.Label(dialog, text="Введите основание (2..16):").pack()
        var = tk.StringVar(value=str(self.controller.base))
        entry = tk.Entry(dialog, textvariable=var)
        entry.pack()
        def apply():
            try:
                new_base = int(var.get())
                if 2 <= new_base <= 16:
                    self.controller.set_base(new_base)
                    self.update_display()
                dialog.destroy()
            except:
                pass
        tk.Button(dialog, text="OK", command=apply).pack()

    def dialog_precision(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Точность")
        tk.Label(dialog, text="Количество цифр после запятой (0..10):").pack()
        var = tk.StringVar(value=str(self.controller.precision))
        entry = tk.Entry(dialog, textvariable=var)
        entry.pack()
        def apply():
            try:
                new_prec = int(var.get())
                if new_prec >= 0:
                    self.controller.set_precision(new_prec)
                    self.update_display()
                dialog.destroy()
            except:
                pass
        tk.Button(dialog, text="OK", command=apply).pack()

    def toggle_real_mode(self):
        self.controller.set_real_mode(self.real_mode_var.get())
        self.update_display()

    def on_button(self, cmd):
        try:
            if cmd == 'C':
                self.controller.clear_all()
                self.update_display()
            elif cmd == 'CE':
                self.controller.clear_entry()
                self.update_display()
            elif cmd == 'MC':
                self.controller.mem_clear()
                self.update_display()
            elif cmd == 'MR':
                self.controller.mem_recall()
                self.update_display()
            elif cmd == 'MS':
                self.controller.mem_store()
                self.update_display()
            elif cmd == 'M+':
                self.controller.mem_add()
                self.update_display()
            elif cmd == '=':
                self.controller.calculate()
                self.update_display()
            elif cmd == '+':
                self.controller.set_operation(TOperation.ADD)
                self.update_display()
            elif cmd == '-':
                self.controller.set_operation(TOperation.SUB)
                self.update_display()
            elif cmd == '*':
                self.controller.set_operation(TOperation.MUL)
                self.update_display()
            elif cmd == '/':
                self.controller.set_operation(TOperation.DIV)
                self.update_display()
            elif cmd == 'Sqr':
                self.controller.apply_function("Sqr")
                self.update_display()
            elif cmd == 'Rev':
                self.controller.apply_function("Rev")
                self.update_display()
            elif cmd == '√':
                self.controller.apply_function("Sqrt")
                self.update_display()
            elif cmd == '⌫':
                self.controller.backspace()
                self.update_display()
            elif cmd == '±':
                self.controller.add_sign()
                self.update_display()
            elif cmd == '.':
                self.controller.add_digit('.')
                self.update_display()
            elif cmd == 'i':
                self.controller.add_digit('i')
                self.update_display()
            elif cmd in '0123456789ABCDEF':
                self.controller.add_digit(cmd)
                self.update_display()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.controller.clear_all()
            self.update_display()

    def on_keypress(self, event):
        key = event.char.upper()
        if key == '\b':
            self.on_button('⌫')
        elif key == '\r':
            self.on_button('=')
        elif key == '-':
            self.on_button('-')
        elif key == '+':
            self.on_button('+')
        elif key == '*':
            self.on_button('*')
        elif key == '/':
            self.on_button('/')
        elif key == '.':
            self.on_button('.')
        elif key == 'C':
            self.on_button('C')
        elif key == 'R':
            self.on_button('Rev')
        elif key == 'Q':
            self.on_button('Sqr')
        elif key == 'S':
            self.on_button('√')
        elif key == 'I':
            self.on_button('i')
        elif key in '0123456789ABCDEF':
            self.on_button(key)

    def copy_to_clipboard(self):
        self.controller.copy_to_clipboard(self.root)
        messagebox.showinfo("Буфер обмена", "Значение скопировано")

    def paste_from_clipboard(self):
        self.controller.paste_from_clipboard(self.root)
        self.update_display()

    def show_about(self):
        messagebox.showinfo("О программе",
                            "Универсальный калькулятор\n"
                            "Режимы:\n"
                            "- p-ичные числа (основание 2..16, кнопки A-F)\n"
                            "- простые дроби (ввод a/b)\n"
                            "- комплексные числа (ввод a+bi, кнопка i)\n"
                            "Операции: +, -, *, /, Sqr, Rev, √\n"
                            "Память: MC, MR, MS, M+\n"
                            "Буфер обмена: Ctrl+C, Ctrl+V\n"
                            "© 2026.\n"
                            "Работу выполнили:\n"
                            "© Кириченко А. А.\n"
                            "    Обидин Н. В. ")

    def show_history(self):
        win = tk.Toplevel(self.root)
        win.title("История вычислений")
        txt = scrolledtext.ScrolledText(win, width=60, height=15)
        txt.pack()
        for entry in self.controller.history:
            txt.insert(tk.END, entry + "\n")
        txt.config(state=tk.DISABLED)