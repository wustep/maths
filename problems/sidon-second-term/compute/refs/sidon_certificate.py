"""Exact rational two-kernel certificate proving C < 0.94601.

The data were obtained from a numerical candidate, but every verification
below uses fractions.Fraction.  The script deliberately avoids ``assert`` so
that all checks remain active under ``python3 -O``.
"""
from fractions import Fraction as F
import hashlib
import math
from pathlib import Path

m = 32
L = 4
n = m * L
T = F(283, 1000)
U = 1 - T
DP = 10**10
DQ = 10**8
S = F(1000000000517, 1000000000000)

P_INTS = [
    28968428, 51751920, 74723226, 99735224, 125402983, 153605108,
    183190707, 216173705, 251799203, 292487097, 338329439, 392967245,
    458879397, 544053990, 660112082, 1127820246,
]

Q1_INTS = [
    5265243, 9406330, 13825964, 18623621, 23733486, 29378188, 35452752,
    42271409, 49760346, 58348570, 68101112, 79698571, 93648749,
    111452356, 135333883, 223692563, 227944859, 150898980, 135288311,
    123589949, 116103341, 109785073, 105499937, 101681059, 99061564,
    96671951, 95093735, 93655995, 92802981, 92122018, 91717199, 92036710,
    91805438, 91421521, 90320299, 90065130, 89727452, 89839755, 89964755,
    90580605, 91160921, 92449547, 93569437, 95915666, 97784094,
    102334914, 105574893, 125502947, 126081891, 108311394, 105988974,
    102370288, 101383342, 99560116, 99121708, 98186781, 98083096,
    97705308, 97853865, 97891151, 98242317, 98646722, 99144578,
    99895302, 100700523, 100111215, 99438010, 99092216, 98592509,
    98465313, 98114482, 98248772, 97986288, 98472870, 98218325,
    99252539, 98887271, 100942328, 100401330, 105545321, 105647811,
    101146408, 101626311, 99873146, 100312755, 99327571, 99654351,
    99113741, 99373614, 99134242, 99366301, 99356351, 99583622,
    99758405, 100021413, 100254056, 100896328, 100502310, 100236358,
    100069507, 99742410, 99748089, 99422734, 99611135, 99240404,
    99685800, 99172368, 100008254, 99233409, 100627825, 99648196,
    101553865, 101517891, 99972813, 100806714, 99611485, 100332611,
    99536861, 100034492, 99552448, 99876233, 99625887, 99830269,
    99755225, 99878644, 99936629, 100004423, 100141934,
]

Q2_INTS = [
    56799440, 56799440, 59436042, 60075672, 62277364, 63357925, 65394187,
    66787231, 68813139, 70468952, 72603664, 74523975, 76904272, 79132562,
    82029485, 84634294, 89030608, 93243409, 96256099, 99178148,
    101855183, 104363112, 106908618, 109188382, 111729191, 113809380,
    116482827, 118287607, 121328282, 122589537, 126649947, 126649947,
    87198981, 87198981, 89447440, 89912801, 91602791, 92258418, 93635693,
    94347931, 95501886, 96187546, 97157361, 97744692, 98531586, 98941631,
    99456142, 99636540, 99214662, 98640671, 98855379, 99089832, 99501868,
    99904163, 100462360, 100893254, 101582945, 101962468, 102807219,
    103051174, 104102438, 104139405, 105336141, 105336141, 96838869,
    96838869, 97554884, 97523833, 98199558, 98250586, 98812765, 98927080,
    99388414, 99520911, 99895893, 100000435, 100282947, 100318323,
    100436888, 100383824, 100036928, 99654425, 99649816, 99622853,
    99701357, 99769424, 99913337, 99992814, 100199759, 100247223,
    100522710, 100508726, 100841272, 100797123, 100996737, 101198905,
    99223578, 99377839, 99467401, 99420471, 99637202, 99584281, 99784776,
    99759617, 99927011, 99917087, 100054668, 100039439, 100145133,
    100100839, 100153491, 99991370, 99941124, 100046309, 100037657,
    100065759, 100046840, 100059631, 100040930, 100044209, 100028065,
    100026101, 100013578, 100009546, 100001652, 99998073, 99995754,
    99994807,
]

EXPECTED_A = F(238055814227338220901, 195312500000000000000)
EXPECTED_B = F(
    367120215488242758713926928814854508645651,
    500000000000000000000000000000000000000000,
)
EXPECTED_MIN_POSITIVE = F(
    246379229716253078971,
    125000000000000000000000000000000,
)
EXPECTED_MIN_POSITIVE_INDEX = 4
TARGET = F(94601, 100000) ** 2


def require(condition: bool, message: object) -> None:
    """Raise an exception if an exact certificate check fails."""
    if not condition:
        raise ArithmeticError(message)


def Q(values: list[F], j: int) -> F:
    return values[j] if 0 <= j < n else F(1)


require(len(P_INTS) == m // 2, "wrong number of entries in P_INTS")
require(len(Q1_INTS) == n, "wrong number of entries in Q1_INTS")
require(len(Q2_INTS) == n, "wrong number of entries in Q2_INTS")

p = [F(x, DP) for x in P_INTS] + [F(x, DP) for x in reversed(P_INTS)]
p2 = [F(1, m)] * m
q1 = [S * F(x, DQ) for x in Q1_INTS]
q2 = [S * F(x, DQ) for x in Q2_INTS]

require(T >= 0 and U >= 0 and T + U == 1, "invalid mixing weights")
require(sum(p) == 1, "the first kernel does not have total mass one")
require(all(x >= 0 for x in p), "the first kernel has a negative entry")
require(
    all(p[i] == p[m - 1 - i] for i in range(m)),
    "the first kernel is not symmetric",
)
require(sum(p2) == 1, "the second kernel does not have total mass one")
require(all(x >= 0 for x in p2), "the second kernel has a negative entry")
require(
    all(p2[i] == p2[m - 1 - i] for i in range(m)),
    "the second kernel is not symmetric",
)

slacks: list[tuple[int, F]] = []
individual_1: list[tuple[int, F]] = []
individual_2: list[tuple[int, F]] = []
for q in range(n + 1):
    cover_1 = sum(p[i] * Q(q1, q + i) for i in range(m))
    cover_2 = sum(p2[i] * Q(q2, q + i) for i in range(m))
    total = T * cover_1 + U * cover_2
    slack = total - 1
    require(slack >= 0, ("covering inequality failed", q, slack))
    slacks.append((q, slack))
    individual_1.append((q, cover_1))
    individual_2.append((q, cover_2))

minimum_index, minimum_slack = min(slacks, key=lambda item: item[1])
positive_slacks = [(q, slack) for q, slack in slacks if slack > 0]
min_positive_index, min_positive_slack = min(
    positive_slacks, key=lambda item: item[1]
)
require(minimum_index == n and minimum_slack == 0, "unexpected zero-slack constraint")
require(
    min_positive_index == EXPECTED_MIN_POSITIVE_INDEX
    and min_positive_slack == EXPECTED_MIN_POSITIVE,
    ("unexpected least positive slack", min_positive_index, min_positive_slack),
)

min_cover_1_index, min_cover_1 = min(individual_1, key=lambda item: item[1])
min_cover_2_index, min_cover_2 = min(individual_2, key=lambda item: item[1])

a = T * m * sum(x * x for x in p) + U * m * sum(x * x for x in p2)
alpha = (T * sum(x * x for x in q1) + U * sum(x * x for x in q2)) / m
b = 1 + 2 * (alpha - L)
C2 = a * b

require(a == EXPECTED_A, ("a differs from the manuscript", a))
require(b == EXPECTED_B, ("b differs from the manuscript", b))
require(b > 0, ("b is not positive", b))
require(C2 < TARGET, ("constant comparison failed", C2, TARGET))

print("minimum constraint index =", minimum_index)
print("minimum slack =", minimum_slack)
print("least positive slack index =", min_positive_index)
print("least positive slack =", min_positive_slack)
print("first-kernel minimum cover index =", min_cover_1_index)
print("first-kernel minimum cover =", min_cover_1)
print("second-kernel minimum cover index =", min_cover_2_index)
print("second-kernel minimum cover =", min_cover_2)
print("a =", a)
print("alpha =", alpha)
print("b =", b)
print("C^2 =", C2)
# Decimal display only; the proof uses the exact comparison C2 < TARGET.
print("C =", math.sqrt(float(C2)))
print("Certified C < 0.94601")

# This final line lets a reader compare the file against the hash printed in
# the manuscript.  It is informational, not one of the mathematical checks.
this_file = Path(__file__)
print("SHA-256 =", hashlib.sha256(this_file.read_bytes()).hexdigest())
