# controller.py (исправленный, полный)
import tkinter as tk
from tkinter import messagebox
from .number import TPNumber, TFrac, TComplex, TANumber
from .memory import TMemory
from .processor import TProcessor, TOperation

class CalculatorController:
    def __init__(self, mode="PNumber", base=10, precision=6, real_mode=True):
        self.mode = mode
        self.base = base
        self.precision = precision
        self.real_mode = real_mode
        self._create_factory()
        self.memory = TMemory()
        self.processor = TProcessor(self._factory)
        self.current = self._factory()
        self._edit_buffer = "0"
        self.waiting_operand = True
        self.last_op = TOperation.NONE
        self._last_rop = None
        self._last_expression = ""
        self.history = []

    def _create_factory(self):
        if self.mode == "PNumber":
            self._factory = lambda: TPNumber(0.0, self.base, self.precision)
        elif self.mode == "TFrac":
            self._factory = lambda: TFrac(0, 1)
        else:
            self._factory = lambda: TComplex(0.0, 0.0, self.base, self.precision)

    def switch_mode(self, new_mode):
        if new_mode == self.mode:
            return
        self.mode = new_mode
        self._create_factory()
        self.clear_all()
        self._edit_buffer = "0"
        self.waiting_operand = True

    def set_base(self, new_base):
        if self.mode in ("PNumber", "TComplex"):
            self.base = new_base
            if self.mode == "PNumber":
                dec_value = self.current.value
                self.current = TPNumber(dec_value, self.base, self.precision)
            else:
                self.current.set_base(new_base)
            self._sync_to_buffer()

    def set_precision(self, new_prec):
        self.precision = new_prec
        if self.mode == "PNumber":
            self.current.precision = new_prec
        elif self.mode == "TComplex":
            self.current.set_precision(new_prec)
        self._sync_to_buffer()

    def set_real_mode(self, real):
        self.real_mode = real
        if self.mode == "PNumber" and not real:
            int_val = int(self.current.value)
            self.current = TPNumber(int_val, self.base, self.precision)
            self._sync_to_buffer()

    def _sync_from_buffer(self):
        try:
            new_num = self._factory()
            new_num.from_string(self._edit_buffer)
            self.current = new_num
        except Exception:
            pass

    def _sync_to_buffer(self):
        self._edit_buffer = self.current.to_string()
        if self.mode == "PNumber" and not self.real_mode and '.' in self._edit_buffer:
            self._edit_buffer = self._edit_buffer.split('.')[0]

    def get_display_string(self) -> str:
        return self._edit_buffer if self._edit_buffer else self.current.to_string()

    def get_expression(self) -> str:
        if self.processor._op != TOperation.NONE:
            left = self.processor._lop_res.to_string() if self.processor._lop_res else ""
            op = self._op_to_str(self.processor._op)
            right = self._edit_buffer if not self.waiting_operand else ""
            if left and op:
                return f"{left} {op} {right}".strip()
        return ""

    def add_digit(self, digit: str):
        if self.waiting_operand:
            self._edit_buffer = ""
            self.waiting_operand = False

        s = self._edit_buffer
        if digit == '.':
            if self.mode != "PNumber" or not self.real_mode:
                return
            if '.' in s:
                return
            if s == "" or s == "-":
                s = "0."
            else:
                s += "."
            self._edit_buffer = s
            self._sync_from_buffer()
            return
        if digit == 'i':
            if self.mode != "TComplex":
                return
            if 'i' in s:
                return
            if s == "" or s == "-":
                s = s + "0i" if s else "0i"
            else:
                s += "i"
            self._edit_buffer = s
            self._sync_from_buffer()
            return
        if self.mode in ("PNumber", "TComplex"):
            try:
                int(digit, self.base)
            except ValueError:
                return
        if self.mode == "TFrac" and digit not in "0123456789":
            return
        if s == "0" and digit != ".":
            s = ""
        s += digit
        self._edit_buffer = s
        self._sync_from_buffer()

    def add_sign(self):
        s = self._edit_buffer
        if s.startswith('-'):
            s = s[1:]
        else:
            s = '-' + s
        self._edit_buffer = s
        self._sync_from_buffer()

    def backspace(self):
        s = self._edit_buffer
        if len(s) == 1 or (s[0] == '-' and len(s) == 2):
            s = "0"
        else:
            s = s[:-1]
            if s == "-" or s == "":
                s = "0"
        self._edit_buffer = s
        self._sync_from_buffer()
        self.waiting_operand = False

    def clear_entry(self):
        self._edit_buffer = "0"
        self.current = self._factory()
        self.waiting_operand = False

    def clear_all(self):
        self.processor.reset()
        self.current = self._factory()
        self._edit_buffer = "0"
        self.waiting_operand = True
        self.last_op = TOperation.NONE
        self._last_rop = None
        self._last_expression = ""

    def mem_store(self):
        self.memory.store(self.current)

    def mem_recall(self):
        num = self.memory.recall()
        if num:
            self.current = num
            self._sync_to_buffer()
            self.waiting_operand = False

    def mem_add(self):
        self.memory.add(self.current)

    def mem_clear(self):
        self.memory.clear()

    def _op_to_str(self, op: int) -> str:
        return {TOperation.ADD: "+", TOperation.SUB: "-", TOperation.MUL: "*", TOperation.DIV: "/"}.get(op, "")

    def set_operation(self, op: int):
        self._sync_from_buffer()
        # Если есть левый операнд и мы не ждём ввод (т.е. правый операнд уже введён),
        # то сначала выполняем текущую операцию, чтобы получить результат.
        if not self.waiting_operand and self.processor._op != TOperation.NONE:
            self._execute_current_operation()
        # Теперь устанавливаем новую операцию
        self.processor.set_left(self.current)
        self.processor.set_operation(op)
        self.last_op = op
        self.waiting_operand = True
        self._last_expression = self.current.to_string() + self._op_to_str(op)

    def _execute_current_operation(self):
        """Выполняет текущую операцию без сброса (используется перед установкой новой операции)."""
        self.processor.set_right(self.current)
        self._last_rop = self.current.copy()
        expr = self._last_expression + self.current.to_string()
        try:
            self.processor.run_operation()
            if self.processor.get_error():
                raise Exception(self.processor.get_error())
            res = self.processor.get_left()
            self.current = res
            self._sync_to_buffer()
            self.processor.clear_operation()
            self.waiting_operand = True
            self._add_history(expr + "=" + self.current.to_string())
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.clear_all()

    def calculate(self):
        """Обработка нажатия '='. Выполняет текущую операцию или повторяет последнюю."""
        self._sync_from_buffer()
        if self.processor._op != TOperation.NONE:
            self._execute_current_operation()
        else:
            # Повтор последней операции
            if self.last_op != TOperation.NONE and self._last_rop is not None:
                self.processor.set_left(self.current)
                self.processor.set_right(self._last_rop)
                self.processor.set_operation(self.last_op)
                expr = self.current.to_string() + self._op_to_str(self.last_op) + self._last_rop.to_string()
                try:
                    self.processor.run_operation()
                    if self.processor.get_error():
                        raise Exception(self.processor.get_error())
                    res = self.processor.get_left()
                    self.current = res
                    self._sync_to_buffer()
                    self.processor.clear_operation()
                    self.waiting_operand = True
                    self._add_history(expr + "=" + self.current.to_string())
                except Exception as e:
                    messagebox.showerror("Ошибка", str(e))
                    self.clear_all()

    def apply_function(self, func: str):
        self._sync_from_buffer()
        self.processor.set_right(self.current)
        try:
            self.processor.run_function(func)
            if self.processor.get_error():
                raise Exception(self.processor.get_error())
            self.current = self.processor.get_right()
            self.waiting_operand = True
            self._sync_to_buffer()
            self._add_history(f"{func}({self._edit_buffer}) = {self.current.to_string()}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.clear_all()

    def _add_history(self, entry: str):
        self.history.append(entry)
        if len(self.history) > 20:
            self.history.pop(0)

    def copy_to_clipboard(self, root):
        root.clipboard_clear()
        root.clipboard_append(self.get_display_string())

    def paste_from_clipboard(self, root):
        try:
            text = root.clipboard_get()
            self._edit_buffer = text
            self._sync_from_buffer()
            self.waiting_operand = False
            self._sync_to_buffer()
        except Exception as e:
            messagebox.showerror("Ошибка вставки", str(e))