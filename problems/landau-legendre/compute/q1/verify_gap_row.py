#!/usr/bin/env python3
"""Replay one reported Oliveira e Silva--Herzog--Pardi prime-gap row."""

from verify_edge import is_prime_u64

LOWER_PRIME = 1_425_172_824_437_699_411
GAP = 1476
UPPER_PRIME = LOWER_PRIME + GAP


def main() -> None:
    if not is_prime_u64(LOWER_PRIME) or not is_prime_u64(UPPER_PRIME):
        raise AssertionError("a reported gap endpoint is not prime")
    for candidate in range(LOWER_PRIME + 2, UPPER_PRIME, 2):
        if is_prime_u64(candidate):
            raise AssertionError(f"interior prime {candidate} breaks the reported gap")
    print(
        "PASS published_gap_row",
        f"lower={LOWER_PRIME}",
        f"gap={GAP}",
        f"upper={UPPER_PRIME}",
    )


if __name__ == "__main__":
    main()
