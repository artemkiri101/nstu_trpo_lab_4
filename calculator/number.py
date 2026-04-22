import math
import re
from abc import ABC, abstractmethod

class TANumber(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass
    @abstractmethod
    def from_string(self, s: str):
        pass
    @abstractmethod
    def copy(self):
        pass
    @abstractmethod
    def add(self, other):
        pass
    @abstractmethod
    def sub(self, other):
        pass
    @abstractmethod
    def mul(self, other):
        pass
    @abstractmethod
    def div(self, other):
        pass
    @abstractmethod
    def sqr(self):
        pass
    @abstractmethod
    def rev(self):
        pass
    @abstractmethod
    def eq_zero(self) -> bool:
        pass
    @abstractmethod
    def set_base(self, base: int):
        pass
    @abstractmethod
    def get_base(self) -> int:
        pass

class TPNumber(TANumber):
    def __init__(self, value: float = 0.0, base: int = 10, precision: int = 6):
        if not (2 <= base <= 16):
            raise ValueError("Основание должно быть от 2 до 16")
        self._base = base
        self._precision = precision
        self._value = float(value)
    @property
    def value(self): return self._value
    @value.setter
    def value(self, v): self._value = v
    @property
    def precision(self): return self._precision
    @precision.setter
    def precision(self, p): self._precision = p
    def to_string(self) -> str:
        if self._value == 0.0:
            return "0"
        digits = "0123456789ABCDEF"
        sign = "-" if self._value < 0 else ""
        val = abs(self._value)
        int_part = int(val)
        frac_part = val - int_part
        if int_part == 0:
            int_str = "0"
        else:
            int_str = ""
            n = int_part
            while n > 0:
                int_str = digits[n % self._base] + int_str
                n //= self._base
        frac_str = ""
        if frac_part > 0 and self._precision > 0:
            frac_str = "."
            f = frac_part
            cnt = 0
            while f > 1e-12 and cnt < self._precision:
                f *= self._base
                digit = int(f)
                frac_str += digits[digit]
                f -= digit
                cnt += 1
        return sign + int_str + frac_str
    def from_string(self, s: str):
        s = s.strip().upper()
        if not s:
            raise ValueError("Пустая строка")
        sign = 1
        if s[0] == '-':
            sign = -1
            s = s[1:]
        if '.' in s:
            int_part_str, frac_part_str = s.split('.')
        else:
            int_part_str, frac_part_str = s, ""
        int_val = 0
        for ch in int_part_str:
            if ch not in "0123456789ABCDEF":
                raise ValueError(f"Недопустимый символ '{ch}'")
            int_val = int_val * self._base + int(ch, self._base)
        frac_val = 0.0
        for i, ch in enumerate(frac_part_str):
            if ch not in "0123456789ABCDEF":
                raise ValueError(f"Недопустимый символ '{ch}'")
            frac_val += int(ch, self._base) / (self._base ** (i + 1))
        self._value = sign * (int_val + frac_val)
    def copy(self): return TPNumber(self._value, self._base, self._precision)
    def add(self, other):
        if not isinstance(other, TPNumber) or other._base != self._base or other._precision != self._precision:
            raise ValueError("Несовместимые операнды")
        return TPNumber(self._value + other._value, self._base, self._precision)
    def sub(self, other):
        if not isinstance(other, TPNumber) or other._base != self._base or other._precision != self._precision:
            raise ValueError("Несовместимые операнды")
        return TPNumber(self._value - other._value, self._base, self._precision)
    def mul(self, other):
        if not isinstance(other, TPNumber) or other._base != self._base or other._precision != self._precision:
            raise ValueError("Несовместимые операнды")
        return TPNumber(self._value * other._value, self._base, self._precision)
    def div(self, other):
        if not isinstance(other, TPNumber) or other._base != self._base or other._precision != self._precision:
            raise ValueError("Несовместимые операнды")
        if other._value == 0:
            raise ZeroDivisionError("Деление на ноль")
        return TPNumber(self._value / other._value, self._base, self._precision)
    def sqr(self): return TPNumber(self._value * self._value, self._base, self._precision)
    def rev(self):
        if self._value == 0:
            raise ZeroDivisionError("Обратное от нуля")
        return TPNumber(1.0 / self._value, self._base, self._precision)
    def sqrt(self):
        if self._value < 0:
            raise ValueError("Корень из отрицательного числа")
        return TPNumber(math.sqrt(self._value), self._base, self._precision)
    def eq_zero(self) -> bool: return abs(self._value) < 1e-12
    def set_base(self, base: int):
        if not (2 <= base <= 16):
            raise ValueError("Основание должно быть от 2 до 16")
        self._base = base
    def get_base(self) -> int: return self._base

class TFrac(TANumber):
    def __init__(self, num: int = 0, den: int = 1):
        if den == 0:
            raise ValueError("Знаменатель не может быть нулём")
        self._num = num
        self._den = den
        self._normalize()
    def _normalize(self):
        if self._den < 0:
            self._num = -self._num
            self._den = -self._den
        g = math.gcd(abs(self._num), self._den)
        self._num //= g
        self._den //= g
    def to_string(self) -> str:
        if self._den == 1:
            return str(self._num)
        return f"{self._num}/{self._den}"
    def from_string(self, s: str):
        s = s.strip()
        if '/' in s:
            parts = s.split('/')
            if len(parts) != 2:
                raise ValueError("Неверный формат дроби")
            num = int(parts[0])
            den = int(parts[1])
        else:
            num = int(s)
            den = 1
        self._num = num
        self._den = den
        self._normalize()
    def copy(self): return TFrac(self._num, self._den)
    def add(self, other):
        if not isinstance(other, TFrac):
            raise TypeError("Операнд должен быть TFrac")
        return TFrac(self._num * other._den + other._num * self._den, self._den * other._den)
    def sub(self, other):
        if not isinstance(other, TFrac):
            raise TypeError("Операнд должен быть TFrac")
        return TFrac(self._num * other._den - other._num * self._den, self._den * other._den)
    def mul(self, other):
        if not isinstance(other, TFrac):
            raise TypeError("Операнд должен быть TFrac")
        return TFrac(self._num * other._num, self._den * other._den)
    def div(self, other):
        if not isinstance(other, TFrac):
            raise TypeError("Операнд должен быть TFrac")
        if other._num == 0:
            raise ZeroDivisionError("Деление на ноль")
        return TFrac(self._num * other._den, self._den * other._num)
    def sqr(self): return TFrac(self._num * self._num, self._den * self._den)
    def rev(self):
        if self._num == 0:
            raise ZeroDivisionError("Обратное от нуля")
        return TFrac(self._den, self._num)
    def eq_zero(self) -> bool: return self._num == 0
    def set_base(self, base: int): pass
    def get_base(self) -> int: return 10

class TComplex(TANumber):
    def __init__(self, re: float = 0.0, im: float = 0.0, base: int = 10, precision: int = 6):
        self._re = TPNumber(re, base, precision)
        self._im = TPNumber(im, base, precision)
    def to_string(self) -> str:
        re_str = self._re.to_string()
        im_val = self._im.value
        if im_val == 0:
            return re_str
        im_str = self._im.to_string()
        if im_val > 0:
            return f"{re_str}+{im_str}i" if re_str != "0" else f"{im_str}i"
        else:
            return f"{re_str}{im_str}i" if re_str != "0" else f"{im_str}i"
    def from_string(self, s: str):
        s = s.strip().replace(' ', '')
        if not s:
            raise ValueError("Пустая строка")
        if 'i' not in s:
            self._re.from_string(s)
            self._im = TPNumber(0.0, self._re.get_base(), self._re.precision)
            return
        # Обработка простых случаев
        if s == 'i':
            self._re = TPNumber(0.0, self._re.get_base(), self._re.precision)
            self._im = TPNumber(1.0, self._re.get_base(), self._re.precision)
            return
        if s == '-i':
            self._re = TPNumber(0.0, self._re.get_base(), self._re.precision)
            self._im = TPNumber(-1.0, self._re.get_base(), self._re.precision)
            return
        if s == '+i':
            self._re = TPNumber(0.0, self._re.get_base(), self._re.precision)
            self._im = TPNumber(1.0, self._re.get_base(), self._re.precision)
            return
        # Разделяем на действительную и мнимую части
        # Убираем последнюю 'i'
        s_without_i = s[:-1]
        # Ищем последний '+' или '-' перед i (не в начале)
        sign_pos = -1
        for idx, ch in enumerate(s_without_i):
            if (ch == '+' or ch == '-') and idx > 0:
                sign_pos = idx
        if sign_pos == -1:
            # только мнимая часть (например "5i")
            self._re = TPNumber(0.0, self._re.get_base(), self._re.precision)
            self._im.from_string(s_without_i)
        else:
            re_part = s_without_i[:sign_pos]
            im_part = s_without_i[sign_pos:]
            self._re.from_string(re_part)
            self._im.from_string(im_part)
    def copy(self): return TComplex(self._re.value, self._im.value, self._re.get_base(), self._re.precision)
    def add(self, other):
        if not isinstance(other, TComplex):
            raise TypeError("Операнд должен быть TComplex")
        return TComplex(self._re.value + other._re.value, self._im.value + other._im.value, self._re.get_base(), self._re.precision)
    def sub(self, other):
        if not isinstance(other, TComplex):
            raise TypeError("Операнд должен быть TComplex")
        return TComplex(self._re.value - other._re.value, self._im.value - other._im.value, self._re.get_base(), self._re.precision)
    def mul(self, other):
        if not isinstance(other, TComplex):
            raise TypeError("Операнд должен быть TComplex")
        a, b = self._re.value, self._im.value
        c, d = other._re.value, other._im.value
        return TComplex(a*c - b*d, a*d + b*c, self._re.get_base(), self._re.precision)
    def div(self, other):
        if not isinstance(other, TComplex):
            raise TypeError("Операнд должен быть TComplex")
        den = other._re.value**2 + other._im.value**2
        if den == 0:
            raise ZeroDivisionError("Деление на ноль")
        a, b = self._re.value, self._im.value
        c, d = other._re.value, other._im.value
        return TComplex((a*c + b*d)/den, (b*c - a*d)/den, self._re.get_base(), self._re.precision)
    def sqr(self):
        a, b = self._re.value, self._im.value
        return TComplex(a*a - b*b, 2*a*b, self._re.get_base(), self._re.precision)
    def rev(self):
        den = self._re.value**2 + self._im.value**2
        if den == 0:
            raise ZeroDivisionError("Обратное от нуля")
        return TComplex(self._re.value/den, -self._im.value/den, self._re.get_base(), self._re.precision)
    def sqrt(self):
        r = math.sqrt(self._re.value**2 + self._im.value**2)
        phi = math.atan2(self._im.value, self._re.value)
        sqrt_r = math.sqrt(r)
        return TComplex(sqrt_r * math.cos(phi/2), sqrt_r * math.sin(phi/2), self._re.get_base(), self._re.precision)
    def eq_zero(self) -> bool: return self._re.eq_zero() and self._im.eq_zero()
    def set_base(self, base: int):
        self._re.set_base(base)
        self._im.set_base(base)
    def get_base(self) -> int: return self._re.get_base()
    def set_precision(self, prec: int):
        self._re.precision = prec
        self._im.precision = prec