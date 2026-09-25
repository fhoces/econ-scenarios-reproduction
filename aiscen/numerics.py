"""Root finding, hand-rolled so the package needs nothing but the standard library.

Every equation the paper solves numerically is one equation in one unknown whose
left-minus-right side is monotone (Proposition 1's capital market, Equation (18);
the actual-economy system (39) with its capital row substituted out; the two
steady-state conditions of Equation (38)). A monotone function crosses zero at most
once, so once a sign change is bracketed, bisection cannot pick the wrong root.
"""


def bisect(f, lo: float, hi: float, tol: float = 1e-14, maxiter: int = 200) -> float:
    """Bisection on a sign change in [lo, hi]: halve the interval, keep the half
    whose ends still differ in sign, stop when it is `tol` wide (relative to the
    size of the root, so 1e-14 means about machine precision)."""
    flo, fhi = f(lo), f(hi)
    if flo == 0.0:
        return lo
    if fhi == 0.0:
        return hi
    if flo * fhi > 0.0:
        # Same sign at both ends: either no root inside, or an even number of them.
        raise ValueError(f"no sign change on [{lo}, {hi}]: f={flo}, {fhi}")
    for _ in range(maxiter):
        mid = 0.5 * (lo + hi)
        fmid = f(mid)
        if fmid == 0.0 or (hi - lo) < tol * max(1.0, abs(mid)):
            return mid
        if flo * fmid < 0.0:        # the sign change is in the left half
            hi, fhi = mid, fmid
        else:                       # ... or in the right half
            lo, flo = mid, fmid
    return 0.5 * (lo + hi)


def expand_and_bisect(f, x0: float, step: float = 0.05, max_expand: int = 200, **kw) -> float:
    """Bracket a root by walking outward from x0, then bisect.

    Used when the root's rough location is unknown but the function is monotone:
    step right by `step`, then left, then further right, and so on, until the two
    ends of the widening interval differ in sign. `step` is chosen per call in the
    units of the unknown (a log change, so 0.01 to 0.05 is a one-to-five percent
    step); a smaller step costs more evaluations but keeps the bracket tight.
    """
    f0 = f(x0)
    lo = hi = x0
    flo = fhi = f0
    for k in range(1, max_expand + 1):
        hi = x0 + k * step                  # try one more step to the right ...
        fhi = f(hi)
        if flo * fhi <= 0.0:
            return bisect(f, lo, hi, **kw)
        lo = x0 - k * step                  # ... then one more step to the left
        flo = f(lo)
        if flo * fhi <= 0.0:
            return bisect(f, lo, hi, **kw)
    raise ValueError("failed to bracket a root")
