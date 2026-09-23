"""The static blocks: Proposition 1 (p. 15) and the actual-economy system (39)
(Table A.1, panel D, p. 43).

Notation follows the paper. Wage variables carrying a tilde are deflated by the
ideas stock A_t, as the system (39) requires; Delta ln w = Delta ln w_tilde
+ Delta ln A.
"""

import math
from dataclasses import dataclass

from .numerics import bisect, expand_and_bisect
from .params import Fixed


# ---------------------------------------------------------------- helpers ----

def bracket_B(f: Fixed, md: float, a: float, psi: float, rho: float) -> float:
    """B_t, the bracket of the labor-share row (14):
        B_t = s_K,t0 + s_L,t0 psi_t m_t d_t (e^{-(1-sigma) a_t} - rho).
    Multiplied by e^{(1-sigma) Delta ln r} it is the capital expenditure share."""
    return f.s_K0 + f.s_L0 * psi * md * (math.exp(-(1.0 - f.sigma) * a) - rho)


def displaced_bracket(f: Fixed, a: float, psi: float, rho: float) -> float:
    """[1 - rho psi - (1 - psi) e^{-(1-sigma) a}], the bracket of (15)."""
    return 1.0 - rho * psi - (1.0 - psi) * math.exp(-(1.0 - f.sigma) * a)


def ell_N_tilde(f: Fixed, md: float, a: float, psi: float, rho: float) -> float:
    """Equation (15): the shift in demand for all-other labor, in logs."""
    return -math.log(1.0 - md * displaced_bracket(f, a, psi, rho))


def Lambda_C(f: Fixed, md: float, a: float, psi: float, rho: float) -> float:
    """Surviving mass of cognitive instances (Table A.1, panel D):
        Lambda_C = s_C,t0/s_L,t0 - m d [1 - rho psi - (1 - psi) e^{-(1-sigma) a}]."""
    return f.cog_share - md * displaced_bracket(f, a, psi, rho)


def tfp_gap(f: Fixed, md: float, a: float, dlnA: float) -> float:
    """Equation (45), the definition of measured TFP used in the simulations."""
    inner = f.s_K0 + f.s_L0 * (1.0 - md * (1.0 - math.exp(-(1.0 - f.sigma) * a))) * \
        math.exp(-(1.0 - f.sigma) * dlnA)
    return -math.log(inner) / (1.0 - f.sigma)


# ------------------------------------------------------- Proposition 1 ----

@dataclass(frozen=True)
class Frictionless:
    """The economy of Section 2.1 at date t: no unemployment, one common wage."""

    dlnr: float
    s_L: float
    dln_sL: float
    dlnw: float          # includes Delta ln A
    dlnw_tilde: float    # deflated by A
    dlnYL: float
    dlnK: float
    ell_N_tilde: float
    l_N_star: float
    l_C_star: float
    dln_tfp: float


def frictionless(f: Fixed, md: float, a: float, psi: float, rho: float,
                 dlnA: float = 0.0) -> Frictionless:
    """Proposition 1: solve the capital market for Delta ln r, then everything else.

    Equation (18) is one monotone equation in one unknown, solved by bisection;
    at eps = infinity the root is zero.
    """
    B = bracket_B(f, md, a, psi, rho)
    lN = ell_N_tilde(f, md, a, psi, rho)
    one_minus_sigma = 1.0 - f.sigma

    def pieces(dlnr: float):
        s_L = 1.0 - B * math.exp(one_minus_sigma * dlnr)          # (14)
        dln_sL = math.log(s_L / f.s_L0)
        dlnw_t = (dln_sL + lN) / one_minus_sigma                  # (16), deflated by A
        dlnw = dlnw_t + dlnA
        dlnYL = dlnw - dln_sL                                     # identity (5)
        dlnK = math.log((1.0 - s_L) / f.s_K0) + dlnYL - dlnr      # (17)
        return s_L, dln_sL, dlnw, dlnw_t, dlnYL, dlnK

    if math.isinf(f.eps):
        dlnr = 0.0
    else:
        # Excess demand for capital: K demanded (17) less K supplied (6). Strictly
        # decreasing in Delta ln r, so bracket outward from zero and bisect.
        dlnr = expand_and_bisect(lambda x: pieces(x)[5] - f.eps * x, 0.0, step=0.02)

    s_L, dln_sL, dlnw, dlnw_t, dlnYL, dlnK = pieces(dlnr)
    lN_star = f.l_N0 * math.exp(lN)
    return Frictionless(
        dlnr=dlnr, s_L=s_L, dln_sL=dln_sL, dlnw=dlnw, dlnw_tilde=dlnw_t,
        dlnYL=dlnYL, dlnK=dlnK, ell_N_tilde=lN,
        l_N_star=lN_star, l_C_star=f.l_C0 + f.l_N0 - lN_star,      # (13)
        dln_tfp=tfp_gap(f, md, a, dlnA),
    )


# --------------------------------------------- the actual economy, (39) ----

@dataclass(frozen=True)
class Actual:
    """The economy at realized employment: prices that make (l_C, l_N) demanded."""

    dlnr: float
    dlnY: float            # Delta ln (Y_t / L_bar), the GDP gap
    dlnw_C_tilde: float    # the A-deflated MPL of AI-sensitive labour at the given employment
    dlnw_N_tilde: float
    s_L: float
    s_C: float
    s_N: float
    s_K: float
    dlnK: float


def _y_of_dlnr(f: Fixed, B: float, dlnr: float, dlnA: float = 0.0) -> float:
    """Capital-market row of (39): capital demanded, s_K,t Y / r, equals capital
    supplied, eps Delta ln r, which in closed form gives the A-deflated output gap

        y_tilde = (eps + sigma) Delta ln r - ln(B / s_K,t0) - Delta ln A,

    where y_tilde = Delta ln(Y_t / L_bar) - Delta ln A. The demand rows of (39)
    are written in A-deflated wages, so they use y_tilde; adding Delta ln A back
    gives the GDP gap. (Checked against Proposition 1 for Delta ln A > 0.)"""
    if math.isinf(f.eps):
        raise ValueError("infinite eps not supported in the actual-economy block")
    return (f.eps + f.sigma) * dlnr - math.log(B / f.s_K0) - dlnA


def _price_index_resid(f: Fixed, LamC: float, B: float, wtC: float, wtN: float,
                       dlnr: float) -> float:
    """First row of (39): the CES price index equals one (the numeraire)."""
    oms = 1.0 - f.sigma
    return (f.s_L0 * LamC * math.exp(oms * wtC)
            + f.s_N0 * math.exp(oms * wtN)
            + B * math.exp(oms * dlnr) - 1.0)


def _wages_at_employment(f: Fixed, LamC: float, y: float, l_C: float, l_N: float) -> tuple:
    """The two labour-demand rows of (39), inverted for the wages that make
    (l_C, l_N) the demanded quantities at the A-deflated output gap y."""
    wtN = (y - math.log(l_N / f.l_N0)) / f.sigma
    wtC = (y + math.log(LamC / f.cog_share) - math.log(l_C / f.l_C0)) / f.sigma
    return wtC, wtN


def actual_at_employment(f: Fixed, md: float, a: float, psi: float, rho: float,
                         l_C: float, l_N: float, dlnA: float = 0.0) -> Actual:
    """Solve (39) for prices and GDP at realized employment (l_C, l_N)."""
    B = bracket_B(f, md, a, psi, rho)
    LamC = Lambda_C(f, md, a, psi, rho)
    oms = 1.0 - f.sigma

    if math.isinf(f.eps):
        # The rental rate is pegged at r_bar, so Delta ln r = 0 and the price index
        # alone pins the output gap; capital is whatever demand calls for.
        def resid_inf(y: float) -> float:
            wtC, wtN = _wages_at_employment(f, LamC, y, l_C, l_N)
            return _price_index_resid(f, LamC, B, wtC, wtN, 0.0)

        y = expand_and_bisect(resid_inf, 0.0, step=0.02)
        wtC, wtN = _wages_at_employment(f, LamC, y, l_C, l_N)
        s_C = f.s_L0 * LamC * math.exp(oms * wtC)
        s_N = f.s_N0 * math.exp(oms * wtN)
        s_K = B
        dlnK = math.log(s_K / f.s_K0) + y + dlnA
        return Actual(dlnr=0.0, dlnY=y + dlnA, dlnw_C_tilde=wtC, dlnw_N_tilde=wtN,
                      s_L=s_C + s_N, s_C=s_C, s_N=s_N, s_K=s_K, dlnK=dlnK)

    def resid(dlnr: float) -> float:
        y = _y_of_dlnr(f, B, dlnr, dlnA)
        wtN = (y - math.log(l_N / f.l_N0)) / f.sigma
        wtC = (y + math.log(LamC / f.cog_share) - math.log(l_C / f.l_C0)) / f.sigma
        return _price_index_resid(f, LamC, B, wtC, wtN, dlnr)

    dlnr = expand_and_bisect(resid, 0.0, step=0.01)
    y = _y_of_dlnr(f, B, dlnr, dlnA)
    wtN = (y - math.log(l_N / f.l_N0)) / f.sigma
    wtC = (y + math.log(LamC / f.cog_share) - math.log(l_C / f.l_C0)) / f.sigma
    oms = 1.0 - f.sigma
    s_C = f.s_L0 * LamC * math.exp(oms * wtC)
    s_N = f.s_N0 * math.exp(oms * wtN)
    s_K = B * math.exp(oms * dlnr)
    return Actual(dlnr=dlnr, dlnY=y + dlnA, dlnw_C_tilde=wtC, dlnw_N_tilde=wtN,
                  s_L=s_C + s_N, s_C=s_C, s_N=s_N, s_K=s_K, dlnK=f.eps * dlnr)


def cognitive_demand(f: Fixed, md: float, a: float, psi: float, rho: float,
                     wtC: float, l_N: float, dlnA: float = 0.0) -> tuple:
    """Solve (39) for l_C at a given cognitive wage: labour demand l^d_C."""
    B = bracket_B(f, md, a, psi, rho)
    LamC = Lambda_C(f, md, a, psi, rho)

    if math.isinf(f.eps):
        def resid_inf(y: float) -> float:
            wtN = (y - math.log(l_N / f.l_N0)) / f.sigma
            return _price_index_resid(f, LamC, B, wtC, wtN, 0.0)

        y = expand_and_bisect(resid_inf, 0.0, step=0.02)
        l_C = f.l_C0 * (LamC / f.cog_share) * math.exp(y - f.sigma * wtC)
        return l_C, y + dlnA, 0.0

    def resid(dlnr: float) -> float:
        y = _y_of_dlnr(f, B, dlnr, dlnA)
        wtN = (y - math.log(l_N / f.l_N0)) / f.sigma
        return _price_index_resid(f, LamC, B, wtC, wtN, dlnr)

    dlnr = expand_and_bisect(resid, 0.0, step=0.01)
    y = _y_of_dlnr(f, B, dlnr, dlnA)
    l_C = f.l_C0 * (LamC / f.cog_share) * math.exp(y - f.sigma * wtC)
    return l_C, y + dlnA, dlnr


# ------------------------------------------- the first-order rows of Table A.1 ----

@dataclass(frozen=True)
class FirstOrder:
    """The 'first order' alternatives to the exact rows of Table A.1, panel B, and
    Equation (11). The paper runs the exact set; these are for intuition and are
    reported alongside the exact solution in the narrative."""

    dlnr: float
    dln_sL: float
    dlnw: float
    dlnYL: float
    ell_N_tilde: float
    dln_tfp: float


def first_order(f: Fixed, md: float, a: float, psi: float, rho: float,
                dlnA: float = 0.0) -> FirstOrder:
    """Equations (11), (19), (26) and the first-order rental row of Table A.1."""
    oms = 1.0 - f.sigma
    dlnr = ((md * a + ((1.0 - rho) - oms * a) * psi * md / f.s_K0 + dlnA)
            / (f.eps + f.sigma / f.s_L0))
    dln_sL = -(1.0 - rho) * psi * md + oms * (psi * md * a - (f.s_K0 / f.s_L0) * dlnr)
    dlnw = md * a + dlnA - (f.s_K0 / f.s_L0) * dlnr
    dlnYL = (md * a + (1.0 - rho) * psi * md - oms * psi * md * a
             - f.sigma * (f.s_K0 / f.s_L0) * dlnr + dlnA)
    lN = (1.0 - rho) * psi * md + oms * (1.0 - psi) * md * a
    return FirstOrder(dlnr=dlnr, dln_sL=dln_sL, dlnw=dlnw, dlnYL=dlnYL,
                      ell_N_tilde=lN, dln_tfp=f.s_L0 * (dlnA + md * a))
