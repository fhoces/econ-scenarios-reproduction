"""Exogenous scenario paths: Equations (8) and (8') of the paper.

m_t and d_t are logistics with a natural ceiling, pinned by the mid-2026 anchor
and the scenario's 2030 value; a_t is linear; psi_t and rho are constant in the
three published scenarios.
"""

import math
from dataclasses import dataclass

from .params import Fixed, Scenario


def logistic_slope(anchor: float, target: float, ceiling: float, years: float) -> float:
    """Equation (8'), p. 26 footnote 11:

        kappa = (1/years) * ln( ((ceiling - anchor)/anchor) * (target/(ceiling - target)) )
    """
    if not (0.0 < anchor < ceiling) or not (0.0 < target < ceiling):
        raise ValueError("anchor and target must lie strictly inside (0, ceiling)")
    return math.log((ceiling - anchor) / anchor * (target / (ceiling - target))) / years


def logistic_midpoint(anchor: float, ceiling: float, kappa: float, t_anchor: float) -> float:
    """Date at which the logistic reaches half its ceiling, from the anchor."""
    return t_anchor - math.log(anchor / (ceiling - anchor)) / kappa


def logistic(t: float, ceiling: float, kappa: float, t_mid: float) -> float:
    """Equation (8): x_t = ceiling / (1 + exp(-kappa (t - t_mid)))."""
    return ceiling / (1.0 + math.exp(-kappa * (t - t_mid)))


@dataclass(frozen=True)
class Paths:
    """Callable bundle of the five exogenous AI objects of Section 2.1.2."""

    fixed: Fixed
    scen: Scenario
    kappa_m: float
    t_mid_m: float
    m_ceiling: float
    kappa_d: float
    t_mid_d: float
    d_ceiling: float

    @classmethod
    def build(cls, fixed: Fixed, scen: Scenario) -> "Paths":
        years = fixed.t_target - fixed.t_anchor          # 3.5
        m_ceiling = fixed.cog_share                      # m_bar = s_C,t0 / s_L,t0, all cognitive work
        kappa_m = logistic_slope(scen.m_anchor, scen.m_2030, m_ceiling, years)
        kappa_d = logistic_slope(scen.d_anchor, scen.d_2030, scen.d_ceiling, years)
        return cls(
            fixed=fixed, scen=scen,
            kappa_m=kappa_m,
            t_mid_m=logistic_midpoint(scen.m_anchor, m_ceiling, kappa_m, fixed.t_anchor),
            m_ceiling=m_ceiling,
            kappa_d=kappa_d,
            t_mid_d=logistic_midpoint(scen.d_anchor, scen.d_ceiling, kappa_d, fixed.t_anchor),
            d_ceiling=scen.d_ceiling,
        )

    def m(self, t: float) -> float:
        return logistic(t, self.m_ceiling, self.kappa_m, self.t_mid_m)

    def d(self, t: float) -> float:
        return logistic(t, self.d_ceiling, self.kappa_d, self.t_mid_d)

    def a(self, t: float) -> float:
        """a_t = a_anchor + g_a (t - t_anchor); Table 1 panel B."""
        return self.scen.a_anchor + self.scen.g_a * (t - self.fixed.t_anchor)

    def psi(self, t: float) -> float:
        return self.scen.psi

    @property
    def rho(self) -> float:
        return self.scen.rho

    def at(self, t: float) -> dict:
        """The five objects at date t, plus the product md that they always enter as."""
        m, d, a, psi = self.m(t), self.d(t), self.a(t), self.psi(t)
        return {"t": t, "m": m, "d": d, "a": a, "psi": psi, "rho": self.rho, "md": m * d}


def research_share(fixed: Fixed, t: float) -> float:
    """iota_R,t on its trend; Equation (41), Appendix C.1. Does not affect the
    gaps (the share is common to the AI and no-AI paths) - reported only."""
    return fixed.iota_R0 * math.exp(fixed.g_iota * (t - fixed.t0))
