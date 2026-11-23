# OEIS A322844, COMMENTS (28 December 2018; 6 January 2019): spectral extensions

Haobo Ma (ChronoAI Pte Ltd, Singapore) and Wenlin Zhang (National University
of Singapore; ChronoAI Pte Ltd, Singapore).

License: Creative Commons Attribution 4.0 International (CC BY 4.0).

## Statement and coverage

`note.tex` proves both conjectures in OEIS A322844, COMMENTS, first posed
in revision 2 (28 December 2018) and revision 5 (6 January 2019).
For the n by n row-serpentine matrix M and n >= 2,

    det(xI-M) = x^(n-2)(x^2-T*x-A),
    T = n(n^2+(n mod 2))/2,
    A = n^2[3(1+n^2)-2(2+n^2)(n mod 2)]/12.

The second exterior trace is -A, and all exterior traces above order two
vanish. The note extends the determinant identity recorded in Spezia's
A317614 (2018); it also proves the arbitrary-row-direction generalization,
even-dimensional eigenvalue formulas, the A246697 row-sum conjectures,
the A317297 bisection, linked matrix sums, a permanent coefficient formula,
the A382597 antidiagonal product and trailing-zero characterization,
generating functions, parity recurrences and reciprocal sums.

The displayed overall exponential function in A322844 has coefficient
a(n)/(n+2)!, rather than the usual a(n)/n!; the note gives both functions
explicitly. Its two displayed subsequence exponential functions use
(2m)! and (2m+1)!, respectively, not m!. The literal row-step parameter in
A317297 gives maximum eigenvalue 26 rather than 34 at parameter 3; using
the actual dimension as row step gives the stated sequence. A cross-reference
to A074147 does not assert the fixed-size-antidiagonal interpretation.

The arithmetic-row rank argument is due to M. Vinay (10 April 2019),
https://math.stackexchange.com/a/3182097 , followed by Rick Wicklin
(8 February 2021),
https://blogs.sas.com/content/iml/2021/02/08/matrix-singular-rows-arithmetic-sequences.html .
It already implies the higher-exterior identity; the note supplies the
explicit characteristic polynomial and signed second coefficient. The
even-order construction and sum identities are credited to De Los Reyes,
Das, Midha and Vellaisamy (2007). The relation of the unavailable mathematical
texts behind the two Miranda construction announcements (2012) to this
spectral coefficient remains unresolved. No priority claim is made.

The note also corrects A246696's even-row odd count to m+1 and proves
its permutation property, and proves the parity and terminal-digit
assertions in A323723 and A323724.

The coverage table in the note distinguishes the posed conjectures, existing
formulas, corrected interpretations and further corollaries.

## Formal statements and written proofs

The following fixed-revision scientific sources identify the formal statements:

- https://github.com/the-omega-institute/trureturing/blob/d9bb8a406783c5222849b798f3c2ab738f653d75/D5/S3/Quantum/Matrix/SpeziaSerpentineSecondExteriorTrace.lean
- https://github.com/the-omega-institute/trureturing/blob/d9bb8a406783c5222849b798f3c2ab738f653d75/D5/S3/Quantum/Matrix/SpeziaSerpentineHigherExteriorTrace.lean

In the first file, `result` proves the absolute second-trace identity for n>1,
and `charpoly_factor` proves the n-to-two characteristic-polynomial reduction
over the rationals for n>=2. In the second file, `result` proves the vanishing
of every exterior trace of order k>2, including k>n. The signed second trace,
explicit quadratic coefficients and further corollaries have written proofs
in the note. The finite comparisons below have their specified finite scope.

## Build the PDF

Use Tectonic 0.17.0:

    tectonic note.tex

Alternatively, use a current LaTeX distribution:

    pdflatex -interaction=nonstopmode -halt-on-error note.tex
    pdflatex -interaction=nonstopmode -halt-on-error note.tex

The bibliography is included in the TeX source; no BibTeX step or additional
figures are needed. `metadata.json` describes the same note, revision 3.

## Exact finite comparisons

Python 3 with its standard library suffices:

    python3 verify.py > computed-checks.json
    python3 -c 'import json; assert json.load(open("computed-checks.json")) == json.load(open("checks.json"))'

The checker compares direct matrix characteristic polynomials through size 24,
principal-minor sums through size 8, power traces through exponent 8,
linear and diagonal sums through size 100, and source sequence prefixes.
It also enumerates all row-direction patterns through size 8, compares
permanents with direct permutation sums through size 8, and checks the
polynomial, triangle, generating-function and partial-fraction identities
over their finite ranges. Further comparisons cover A246696's 101 initial
rows, 5,151 distinct values in their two parity intervals, 50 paired-row intervals, and the
first off-diagonal parity and terminal-digit statements through dimension 100.
`checks.json` records the exact counts.

`reference-values.json` contains the cited OEIS values and source identifiers.
All claims for unbounded matrix sizes and infinite series rely on the written
proofs, not an extrapolation from these finite comparisons.

`SHA256SUMS` lists the exact source-file digests; on systems with GNU coreutils,
use `sha256sum -c SHA256SUMS` to compare them.
