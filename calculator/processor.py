class TOperation:
    NONE, ADD, SUB, MUL, DIV = range(5)

class TProcessor:
    def __init__(self, number_factory):
        """number_factory - функция, создающая экземпляр TANumber по умолчанию (0)."""
        self._factory = number_factory
        self._lop_res = None   # левый операнд / результат
        self._rop = None       # правый операнд
        self._op = TOperation.NONE
        self._error = ""
    
    def reset(self):
        self._lop_res = self._factory()
        self._rop = self._factory()
        self._op = TOperation.NONE
        self._error = ""
    
    def set_operation(self, op: int):
        self._op = op
    
    def clear_operation(self):
        self._op = TOperation.NONE
    
    def set_left(self, num):
        self._lop_res = num.copy()
    
    def set_right(self, num):
        self._rop = num.copy()
    
    def get_left(self):
        return self._lop_res.copy() if self._lop_res else None
    
    def get_right(self):
        return self._rop.copy() if self._rop else None
    
    def run_operation(self):
        if self._op == TOperation.NONE:
            return
        if self._lop_res is None or self._rop is None:
            self._error = "Операнды не установлены"
            return
        try:
            if self._op == TOperation.ADD:
                res = self._lop_res.add(self._rop)
            elif self._op == TOperation.SUB:
                res = self._lop_res.sub(self._rop)
            elif self._op == TOperation.MUL:
                res = self._lop_res.mul(self._rop)
            elif self._op == TOperation.DIV:
                res = self._lop_res.div(self._rop)
            else:
                return
            self._lop_res = res
            self._error = ""
        except Exception as e:
            self._error = str(e)
    
    def run_function(self, func: str):
        if self._rop is None:
            self._error = "Нет правого операнда"
            return
        try:
            if func == "Sqr":
                self._rop = self._rop.sqr()
            elif func == "Rev":
                self._rop = self._rop.rev()
            elif func == "Sqrt":
                if hasattr(self._rop, 'sqrt'):
                    self._rop = self._rop.sqrt()
                else:
                    self._error = "Корень не поддерживается для данного типа чисел"
            self._error = ""
        except Exception as e:
            self._error = str(e)
    
    def get_error(self) -> str:
        return self._error