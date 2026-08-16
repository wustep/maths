"""Shared van der Waerden W(2,7) helpers.

A coloring is a list of 0/1 values for [1, n] (index 0 unused, or a 0-based
list of length n). Verifiers always enumerate every 7-AP in the interval.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence


def legendre(a: int, p: int) -> int:
    """Legendre symbol (a/p) in {-1, 0, 1}."""
    return pow(a % p, (p - 1) // 2, p) - p * (pow(a % p, (p - 1) // 2, p) == p - 1)


def quadratic_residue_cycle(p: int, zero_color: int = 0) -> list[int]:
    """2-coloring of Z/pZ: residues=0, nonresidues=1, 0 -> zero_color."""
    colors = [zero_color]
    for a in range(1, p):
        colors.append(0 if pow(a, (p - 1) // 2, p) == 1 else 1)
    return colors


def max_monochrome_run(colors: Sequence[int], cyclic: bool = False) -> int:
    n = len(colors)
    if n == 0:
        return 0
    best = 1
    run = 1
    for i in range(1, n):
        if colors[i] == colors[i - 1]:
            run += 1
            if run > best:
                best = run
        else:
            run = 1
    if cyclic and n > 1 and colors[0] == colors[-1]:
        left = 1
        while left < n and colors[left] == colors[0]:
            left += 1
        right = 1
        while right < n and colors[n - 1 - right] == colors[-1]:
            right += 1
        best = max(best, min(n, left + right))
    return best


def first_mono_ap(
    colors: Sequence[int],
    k: int = 7,
    cyclic: bool = False,
) -> tuple[int, int] | None:
    """Return (start, diff) of the first monochromatic k-AP, or None.

    Linear: positions in [0, n). Cyclic: wrap modulo n; only APs with k
    distinct points are considered.
    """
    n = len(colors)
    if cyclic:
        for d in range(1, n):
            for a in range(n):
                pts = [(a + i * d) % n for i in range(k)]
                if len(set(pts)) < k:
                    continue
                c0 = colors[pts[0]]
                if all(colors[p] == c0 for p in pts[1:]):
                    return a, d
        return None

    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        last_start = n - (k - 1) * d
        for a in range(last_start):
            c0 = colors[a]
            if all(colors[a + i * d] == c0 for i in range(1, k)):
                return a, d
    return None


def count_mono_aps(colors: Sequence[int], k: int = 7) -> int:
    n = len(colors)
    count = 0
    max_d = (n - 1) // (k - 1)
    for d in range(1, max_d + 1):
        last_start = n - (k - 1) * d
        for a in range(last_start):
            c0 = colors[a]
            if all(colors[a + i * d] == c0 for i in range(1, k)):
                count += 1
    return count


def enumerate_new_aps_through(
    n: int,
    point: int,
    k: int = 7,
) -> Iterable[tuple[int, ...]]:
    """k-APs in [0, n) that contain `point` and are not contained in [0, n-1)."""
    # point is the last index n-1 when extending.
    for i in range(k):
        # point = a + i*d, 0 <= a, a+(k-1)d < n
        # a = point - i*d >= 0, a+(k-1)d = point + (k-1-i)*d < n
        max_d_left = point // i if i else n
        max_d_right = (n - 1 - point) // (k - 1 - i) if i < k - 1 else n
        max_d = min(max_d_left, max_d_right)
        for d in range(1, max_d + 1):
            a = point - i * d
            yield tuple(a + t * d for t in range(k))


def can_color_extension(prefix: Sequence[int], k: int = 7) -> list[int]:
    """Which colors in {0,1} can be appended without a mono k-AP."""
    n = len(prefix) + 1
    point = n - 1
    ok = []
    for color in (0, 1):
        colors = list(prefix) + [color]
        blocked = False
        for ap in enumerate_new_aps_through(n, point, k):
            c0 = colors[ap[0]]
            if all(colors[j] == c0 for j in ap[1:]):
                blocked = True
                break
        if not blocked:
            ok.append(color)
    return ok


def repeat_cycle(cycle: Sequence[int], copies: int, extra: list[int] | None = None) -> list[int]:
    colors = list(cycle) * copies
    if extra:
        colors.extend(extra)
    return colors


def parse_ab(text: str) -> list[int]:
    return [ord(c) - ord("a") for c in text.strip() if c in "ab"]


def format_ab(colors: Sequence[int]) -> str:
    return "".join("ab"[c] for c in colors)


def parse_bits(text: str) -> list[int]:
    text = text.strip()
    if text and all(c in "abAB" for c in text.replace("\n", "").replace(" ", "")):
        return parse_ab(text)
    bits: list[int] = []
    for token in text.replace(",", " ").split():
        if token in ("0", "1"):
            bits.append(int(token))
        elif token in ("a", "A"):
            bits.append(0)
        elif token in ("b", "B"):
            bits.append(1)
    if bits:
        return bits
    compact = "".join(ch for ch in text if ch in "01")
    return [int(ch) for ch in compact]


def load_coloring(path: str) -> list[int]:
    with open(path, encoding="ascii") as handle:
        return parse_bits(handle.read())
