# Source of the n=71 certificate

Retrieved on 23 August 2026 from Achim Flammenkamp's
[no-three-in-line database](https://wwwhomes.uni-bielefeld.de/achim/no3in/readme.html).
Its dated notes say that Marijn Heule found the first $n=71$ solution on
17 August 2026 in symmetry class `rct4`.

The exact entry came from the database lookup endpoint
`/cgi-bin/cgiwrap/achim/script_lookup?para=FIXED`, with POST fields
`symm=c`, `size=71`, and `index=1`. The response identified it as the first
`rct4` solution and reported database cut date 19 August 2026. The untouched
one-line code is [`n71-rct4.code`](n71-rct4.code).

The database documentation specifies one symmetry character followed by two
encoded column positions for each row. Its current 90-character alphabet is
recorded in `decode_database.py`; that decoder rejects wrong lengths,
out-of-grid columns, and duplicate row positions before emitting the plain
coordinate certificate.
