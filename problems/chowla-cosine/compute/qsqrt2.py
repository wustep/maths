"""Exact arithmetic in Q(sqrt(2)) and C tensor Q(sqrt(2)).

Used to certify Bedert Lemma 7.2 (and variant auxiliaries whose
angles live in {0, pi/4, pi/2, ...}) without floating point.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Tuple


class QSqrt2:
    """a + b*sqrt(2) with a, b rational."""

    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = a if isinstance(a, Fraction) else Fraction(a)
        self.b = b if isinstance(b, Fraction) else Fraction(b)

    def __repr__(self) -> str:
        return f"QSqrt2({self.a}, {self.b})"

    def __str__(self) -> str:
        if self.b == 0:
            return str(self.a)
        if self.a == 0:
            return f"{self.b}*sqrt(2)"
        sign = "+" if self.b >= 0 else "-"
        return f"{self.a} {sign} {abs(self.b)}*sqrt(2)"

    def __eq__(self, other) -> bool:
        other = _as_q(other)
        return self.a == other.a and self.b == other.b

    def __hash__(self) -> int:
        return hash((self.a, self.b))

    def __neg__(self) -> "QSqrt2":
        return QSqrt2(-self.a, -self.b)

    def __add__(self, other) -> "QSqrt2":
        other = _as_q(other)
        return QSqrt2(self.a + other.a, self.b + other.b)

    def __radd__(self, other) -> "QSqrt2":
        return self + other

    def __sub__(self, other) -> "QSqrt2":
        other = _as_q(other)
        return QSqrt2(self.a - other.a, self.b - other.b)

    def __rsub__(self, other) -> "QSqrt2":
        return _as_q(other) - self

    def __mul__(self, other) -> "QSqrt2":
        other = _as_q(other)
        # (a+b√2)(c+d√2) = (ac+2bd) + (ad+bc)√2
        return QSqrt2(self.a * other.a + 2 * self.b * other.b, self.a * other.b + self.b * other.a)

    def __rmul__(self, other) -> "QSqrt2":
        return self * other

    def __truediv__(self, other) -> "QSqrt2":
        other = _as_q(other)
        # 1/(c+d√2) = (c-d√2)/(c^2-2d^2)
        den = other.a * other.a - 2 * other.b * other.b
        if den == 0:
            raise ZeroDivisionError(other)
        conj = QSqrt2(other.a, -other.b)
        num = self * conj
        return QSqrt2(num.a / den, num.b / den)

    def __abs__(self) -> "QSqrt2":
        # only used when the number is rational or we compare via to_float
        if self.b == 0:
            return QSqrt2(abs(self.a), 0)
        raise ValueError("abs of irrational QSqrt2 is not in Q(sqrt(2)) in general")

    def to_float(self) -> float:
        return float(self.a) + float(self.b) * (2.0**0.5)

    def sign(self) -> int:
        """Sign of a+b√2. Uses exact comparison against 0."""
        if self.a == 0 and self.b == 0:
            return 0
        # a + b√2 > 0?
        if self.b == 0:
            return 1 if self.a > 0 else -1
        if self.a >= 0 and self.b >= 0:
            return 1
        if self.a <= 0 and self.b <= 0:
            return -1
        # opposite signs: a + b√2 > 0 iff
        # if b>0: √2 > -a/b iff 2 > (a/b)^2 and -a/b > 0, or always if -a/b <= 0
        # Compare (a)^2 ? 2 b^2, taking signs into account.
        # a + b√2 > 0 iff (if b>0) √2 > -a/b; if a>=0 this is true.
        left = self.a * self.a
        right = 2 * self.b * self.b
        if self.b > 0:
            # √2 > -a/b. If -a/b <= 0 i.e. a>=0, true.
            if self.a >= 0:
                return 1
            # a<0, b>0: true iff 2 > a^2/b^2 i.e. 2b^2 > a^2
            return 1 if right > left else (-1 if right < left else 0)
        else:
            # b<0: a + b√2 > 0 iff a > (-b)√2 > 0 so a must be >0, and a^2 > 2b^2
            if self.a <= 0:
                return -1
            return 1 if left > right else (-1 if left < right else 0)

    def __lt__(self, other) -> bool:
        return (self - other).sign() < 0

    def __le__(self, other) -> bool:
        return (self - other).sign() <= 0

    def __gt__(self, other) -> bool:
        return (self - other).sign() > 0

    def __ge__(self, other) -> bool:
        return (self - other).sign() >= 0

    def as_pair(self) -> Tuple[Fraction, Fraction]:
        return (self.a, self.b)


def _as_q(x) -> QSqrt2:
    if isinstance(x, QSqrt2):
        return x
    return QSqrt2(x, 0)


SQRT2 = QSqrt2(0, 1)
ZERO = QSqrt2(0, 0)
ONE = QSqrt2(1, 0)


class CSqrt2:
    """Complex numbers with coefficients in Q(sqrt(2))."""

    __slots__ = ("re", "im")

    def __init__(self, re=0, im=0):
        self.re = re if isinstance(re, QSqrt2) else _as_q(re)
        self.im = im if isinstance(im, QSqrt2) else _as_q(im)

    def __repr__(self) -> str:
        return f"CSqrt2({self.re!r}, {self.im!r})"

    def __str__(self) -> str:
        return f"({self.re}) + ({self.im}) i"

    def __eq__(self, other) -> bool:
        other = _as_c(other)
        return self.re == other.re and self.im == other.im

    def __neg__(self) -> "CSqrt2":
        return CSqrt2(-self.re, -self.im)

    def __add__(self, other) -> "CSqrt2":
        other = _as_c(other)
        return CSqrt2(self.re + other.re, self.im + other.im)

    def __radd__(self, other) -> "CSqrt2":
        return self + other

    def __sub__(self, other) -> "CSqrt2":
        other = _as_c(other)
        return CSqrt2(self.re - other.re, self.im - other.im)

    def __rsub__(self, other) -> "CSqrt2":
        return _as_c(other) - self

    def __mul__(self, other) -> "CSqrt2":
        other = _as_c(other)
        return CSqrt2(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re,
        )

    def __rmul__(self, other) -> "CSqrt2":
        return self * other

    def __truediv__(self, other) -> "CSqrt2":
        other = _as_c(other)
        den = other.re * other.re + other.im * other.im
        conj = CSqrt2(other.re, -other.im)
        num = self * conj
        return CSqrt2(num.re / den, num.im / den)

    def conj(self) -> "CSqrt2":
        return CSqrt2(self.re, -self.im)

    def to_complex(self) -> complex:
        return complex(self.re.to_float(), self.im.to_float())


def _as_c(x) -> CSqrt2:
    if isinstance(x, CSqrt2):
        return x
    if isinstance(x, QSqrt2):
        return CSqrt2(x, ZERO)
    if isinstance(x, complex):
        raise TypeError("refuse implicit float complex")
    return CSqrt2(_as_q(x), ZERO)


I = CSqrt2(ZERO, ONE)
