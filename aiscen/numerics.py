"""Root finding, hand-rolled so the package needs nothing but the standard library."""


def bisect(f, lo: float, hi: float, tol: float = 1e-14, maxiter: int = 200) -> float:
    """Bisection on a sign change in [lo, hi]."""
    flo, fhi = f(lo), f(hi)
    if flo == 0.0:
        return lo
    if fhi == 0.0:
        return hi
    if flo * fhi > 0.0:
        raise ValueError(f"no sign change on [{lo}, {hi}]: f={flo}, {fhi}")
    for _ in range(maxiter):
        mid = 0.5 * (lo + hi)
        fmid = f(mid)
        if fmid == 0.0 or (hi - lo) < tol * max(1.0, abs(mid)):
            return mid
        if flo * fmid < 0.0:
            hi, fhi = mid, fmid
        else:
            lo, flo = mid, fmid
    return 0.5 * (lo + hi)


def expand_and_bisect(f, x0: float, step: float = 0.05, max_expand: int = 200, **kw) -> float:
    """Bracket a root by walking outward from x0, then bisect."""
    f0 = f(x0)
    lo = hi = x0
    flo = fhi = f0
    for k in range(1, max_expand + 1):
        hi = x0 + k * step
        fhi = f(hi)
        if flo * fhi <= 0.0:
            return bisect(f, lo, hi, **kw)
        lo = x0 - k * step
        flo = f(lo)
        if flo * fhi <= 0.0:
            return bisect(f, lo, hi, **kw)
    raise ValueError("failed to bracket a root")
