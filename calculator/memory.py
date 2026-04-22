class TMemory:
    def __init__(self):
        self._number = None
        self._state = False
    def store(self, num):
        self._number = num.copy()
        self._state = True
    def recall(self):
        if self._number is None:
            return None
        return self._number.copy()
    def add(self, num):
        if self._number is None:
            self._number = num.copy()
        else:
            self._number = self._number.add(num)
        self._state = True
    def clear(self):
        self._number = None
        self._state = False
    def state_string(self) -> str:
        return "M" if self._state else " "