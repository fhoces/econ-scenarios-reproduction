"""Panel E of Table A.1: the normal-times steady state, solved once at t0.

Ten conditions for nine objects, one redundant (the finding-rate conditions pin
the pools only up to scale; adding-up fixes it). Equation (38), p. 21.
"""

from dataclasses import dataclass

from .numerics import bisect
from .params import Fixed


@dataclass(frozen=True)
class SteadyState:
    """The normal-times labor market of Equation (38): the pool split by origin,
    hires, effective search, finding and filling rates, matching efficiency and the
    quit rates, all per month and in shares of the labor force."""

    U_C: float      # pool of cognitive origin, share of L
    U_N: float      # pool of all-other origin
    H_C: float      # hires per month
    H_N: float
    S_C: float      # effective search directed at each group
    S_N: float
    f_C: float      # finding rate by origin, per month
    f_N: float
    pi_C: float     # filling rate, per month
    pi_N: float
    chi: float      # matching efficiency
    q_C: float      # quit rates, per month
    q_N: float

    @property
    def f_agg(self) -> float:
        """Aggregate finding rate implied by the pool."""
        return (self.H_C + self.H_N) / (self.U_C + self.U_N)

    @property
    def switch_share(self) -> float:
        """Share of job-finders who change group; calibration target 1/7."""
        cross = (self.H_N / self.S_N) * self.U_C + (self.H_C / self.S_C) * self.U_N
        return 0.0 if cross == 0 else (cross * self.mu_bar_used) / (self.H_C + self.H_N)

    mu_bar_used: float = 0.17


def effective_search(U_C: float, U_N: float, mu: float) -> tuple:
    """Equation (33): S_C = U_C + mu U_N, S_N = mu U_C + U_N."""
    return U_C + mu * U_N, mu * U_C + U_N


def solve(fixed: Fixed) -> SteadyState:
    """Solve Equation (38) at the normal-times search discount mu_bar."""
    mu = fixed.mu_bar
    q_C, q_N = fixed.q_bar_C, fixed.q_bar_N
    H_C, H_N = q_C * fixed.l_C0, q_N * fixed.l_N0     # hiring replaces quits

    # Split the pool between the two origins. The unknown is U_C (then U_N is the
    # rest of U_bar by adding-up); the condition is the cognitive origin's flow
    # balance, f_C U_C = H_C: hires from that pool equal the quits into it. The
    # residual is written as f_C - H_C / U_C, which falls from +inf (U_C near 0,
    # so H_C / U_C is huge) to below zero (U_C near U_bar), so the bracket just
    # stays a hair inside (0, U_bar) and the root is unique.
    def resid(U_C: float) -> float:
        U_N = fixed.U_bar - U_C
        S_C, S_N = effective_search(U_C, U_N, mu)
        f_C = H_C / S_C + mu * H_N / S_N              # (35) at the steady state
        return f_C - H_C / U_C                        # f_C U_C = H_C

    U_C = bisect(resid, 1e-8, fixed.U_bar - 1e-8)
    U_N = fixed.U_bar - U_C
    S_C, S_N = effective_search(U_C, U_N, mu)
    f_C = H_C / S_C + mu * H_N / S_N
    f_N = mu * H_C / S_C + H_N / S_N

    # Matching efficiency chi, from the employment-weighted mean filling rate.
    def fill(chi: float, H: float, S: float) -> float:
        """Invert the matching function: pi = chi [1 - (H/(chi S))^iota]^(1/iota)."""
        x = H / (chi * S)
        if x >= 1.0:
            return float("nan")
        return chi * (1.0 - x ** fixed.iota_match) ** (1.0 / fixed.iota_match)

    def fill_resid(chi: float) -> float:
        pi_C, pi_N = fill(chi, H_C, S_C), fill(chi, H_N, S_N)
        mean = (fixed.l_C0 * pi_C + fixed.l_N0 * pi_N) / fixed.L_emp0
        return mean - fixed.fill_bar

    # Bracket for chi. Lower end: the inversion needs H/(chi S) < 1 for both
    # groups ("a solution as long as normal hiring per unit of effective search is
    # below the ceiling chi", p. 21), so start a hair above the larger of the two
    # ratios. Upper end: chi <= 1 by definition of the matching function (p. 20 and
    # its footnote 8; den Haan et al. set chi = 1). The mean filling rate rises
    # with chi, so the residual has one sign change in between. The paper's value
    # is 0.76.
    lo = max(H_C / S_C, H_N / S_N) * 1.000001          # chi must exceed hires per searcher
    chi = bisect(fill_resid, lo, 1.0)
    ss = SteadyState(
        U_C=U_C, U_N=U_N, H_C=H_C, H_N=H_N, S_C=S_C, S_N=S_N,
        f_C=f_C, f_N=f_N, pi_C=fill(chi, H_C, S_C), pi_N=fill(chi, H_N, S_N),
        chi=chi, q_C=q_C, q_N=q_N, mu_bar_used=mu,
    )
    return ss


def check_redundant_condition(fixed: Fixed, ss: SteadyState) -> float:
    """The other origin's flow-balance condition, which should hold automatically."""
    return ss.f_N - ss.H_N / ss.U_N
