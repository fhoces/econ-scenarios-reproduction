"""The monthly simulation: steps 1-9 of Appendix A (pp. 40-41) over the 44-equation
system of Table A.1.

Everything is a gap against the no-AI path, which grows at g (ideas), g (wage and
output per worker), g + n (GDP). Head counts are shares of the labor force.
"""

import math
from dataclasses import dataclass, field

from . import statics, steady
from .params import Fixed, Scenario
from .paths import Paths


@dataclass
class Month:
    """One row of the simulated path: everything Table A.1 names, per month."""

    t: float
    # exogenous paths
    m: float = 0.0
    d: float = 0.0
    a: float = 0.0
    psi: float = 0.0
    # ideas block (panel A)
    dlnA: float = 0.0
    dlnR: float = 0.0
    dg: float = 0.0
    # frictionless / target economy (panel B)
    dlnr_star: float = 0.0
    s_L_star: float = 0.0
    dlnw_common: float = 0.0
    dlnYL_star: float = 0.0
    ell_N_tilde: float = 0.0
    l_C_star: float = 0.0
    l_N_star: float = 0.0
    dln_tfp: float = 0.0
    # flows (panel C)
    l_C: float = 0.0
    l_N: float = 0.0
    U_C: float = 0.0
    U_N: float = 0.0
    G_C: float = 0.0
    B_N: float = 0.0
    q_C: float = 0.0
    q_N: float = 0.0
    N_C: float = 0.0
    x_C: float = 0.0            # ln(w_C,t / w_t), the rigid cognitive discount
    dlnw_C_clear: float = 0.0
    l_C_demand: float = 0.0
    E: float = 0.0
    Z: float = 0.0
    D_C: float = 0.0
    v_C: float = 0.0
    v_N: float = 0.0
    S_C: float = 0.0
    S_N: float = 0.0
    H_C: float = 0.0
    H_N: float = 0.0
    f_C: float = 0.0
    f_N: float = 0.0
    # reporting (panel D), the actual economy at realized employment
    dlnY: float = 0.0
    dlnw_C_paid: float = 0.0
    dlnw_C_mpl: float = 0.0
    dlnw_N: float = 0.0
    dlnw_avg: float = 0.0
    dlnr: float = 0.0
    dlnK: float = 0.0
    s_L: float = 0.0
    u_excess: float = 0.0
    u_rate: float = 0.0
    u_rate_C: float = 0.0
    u_rate_N: float = 0.0
    reallocation: float = 0.0
    overhang: float = 0.0
    cog_shift: float = 0.0


@dataclass
class Result:
    fixed: Fixed
    scen: Scenario
    paths: Paths
    ss: steady.SteadyState
    months: list = field(default_factory=list)

    def at(self, t: float) -> Month:
        """The row closest to date t."""
        return min(self.months, key=lambda r: abs(r.t - t))

    def series(self, name: str) -> list:
        return [getattr(r, name) for r in self.months]

    def growth(self, name: str, t: float, months: int = 12) -> float:
        """Log change in a gap-plus-trend series over the preceding `months`."""
        i = self.months.index(self.at(t))
        return getattr(self.months[i], name) - getattr(self.months[i - months], name)


def run(fixed: Fixed, scen: Scenario, t_end: float = 2030.0) -> Result:
    """Simulate one scenario from t0 to t_end on a monthly grid."""
    f, h = fixed, fixed.h
    p = Paths.build(f, scen)
    ss = steady.solve(f)
    res = Result(fixed=f, scen=scen, paths=p, ss=ss)

    xi_m = f.xi ** (1.0 / 12.0)
    qX = {"C": (1.0 - f.q_resp_share) * ss.q_C, "N": (1.0 - f.q_resp_share) * ss.q_N}
    qT = {"C": f.q_resp_share * ss.q_C, "N": f.q_resp_share * ss.q_N}

    # State, predetermined at t0 (Table A.1 notes, p. 43)
    dlnA = 0.0
    l_C, l_N = f.l_C0, f.l_N0
    U_C, U_N = ss.U_C, ss.U_N
    f_C_lag, f_N_lag = ss.f_C, ss.f_N
    x_C = 0.0                                  # w_C,t0-1 = w_t0-1

    n_months = int(round((t_end - f.t0) * 12)) + 1
    for k in range(n_months):
        t = f.t0 + k * h
        row = Month(t=t)
        xt = p.at(t)
        xt1 = p.at(t + h)
        row.m, row.d, row.a, row.psi = xt["m"], xt["d"], xt["a"], xt["psi"]
        row.dlnA = dlnA

        # 2-3. Capital market, wage, shares and targets (Proposition 1) at t ...
        fr = statics.frictionless(f, xt["md"], xt["a"], xt["psi"], xt["rho"], dlnA)
        row.dlnr_star, row.s_L_star = fr.dlnr, fr.s_L
        row.dlnw_common, row.dlnYL_star = fr.dlnw, fr.dlnYL
        row.ell_N_tilde, row.dln_tfp = fr.ell_N_tilde, fr.dln_tfp
        row.l_C_star, row.l_N_star = fr.l_C_star, fr.l_N_star
        # ... and the date-(t+1) targets, which need no rental rate (Table A.1 notes)
        lN_tilde_next = statics.ell_N_tilde(f, xt1["md"], xt1["a"], xt1["psi"], xt1["rho"])
        l_N_star_next = f.l_N0 * math.exp(lN_tilde_next)
        l_C_star_next = f.l_C0 + f.l_N0 - l_N_star_next

        # 4. Gaps and the cognitive wage
        row.l_C, row.l_N, row.U_C, row.U_N = l_C, l_N, U_C, U_N
        row.G_C = max(0.0, math.log(l_C) - math.log(l_C_star_next))          # (28)
        row.B_N = max(0.0, math.log(l_N_star_next) - math.log(l_N))          # (28)
        row.N_C = l_C + max(0.0, U_C - ss.U_C)                               # (29)
        clear = statics.actual_at_employment(f, xt["md"], xt["a"], xt["psi"], xt["rho"],
                                            row.N_C, l_N, dlnA)              # w^c_C by (39)
        row.dlnw_C_clear = clear.dlnw_C_tilde + dlnA
        # (30): the discount to the common wage closes a fraction of its gap
        x_C = xi_m * x_C + (1.0 - xi_m) * (clear.dlnw_C_tilde - fr.dlnw_tilde)
        row.x_C = x_C
        wtC = fr.dlnw_tilde + x_C                                            # A-deflated
        row.dlnw_C_paid = wtC + dlnA
        l_C_d, _, _ = statics.cognitive_demand(f, xt["md"], xt["a"], xt["psi"], xt["rho"],
                                               wtC, l_N, dlnA)
        row.l_C_demand = l_C_d
        row.E = max(0.0, l_C - l_C_d)
        row.Z = max(0.0, l_C_d - l_C)

        # 5. Separations and openings
        row.q_C = qX["C"] + qT["C"] * f_C_lag / ss.f_C                       # (27)
        row.q_N = qX["N"] + qT["N"] * f_N_lag / ss.f_N
        row.D_C = max(0.0, row.E - row.q_C * l_C)                            # (31)
        row.v_C = (max(0.0, row.q_C * l_C - row.E) + scen.theta_H * row.Z) / ss.pi_C
        row.v_N = (row.q_N + scen.theta_H * row.B_N) * l_N / ss.pi_N         # (32)

        # 6. Matching
        row.S_C, row.S_N = steady.effective_search(U_C, U_N, scen.mu)        # (33)
        iota = f.iota_match
        def hires(S: float, v: float) -> float:                              # (34)
            if S <= 0.0 or v <= 0.0:
                return 0.0
            return ss.chi * S * v / (S ** iota + v ** iota) ** (1.0 / iota)
        row.H_C, row.H_N = hires(row.S_C, row.v_C), hires(row.S_N, row.v_N)
        hC = row.H_C / row.S_C if row.S_C > 0 else 0.0
        hN = row.H_N / row.S_N if row.S_N > 0 else 0.0
        row.f_C = hC + scen.mu * hN                                          # (35)
        row.f_N = scen.mu * hC + hN

        # 8. Reporting: the actual economy at realized employment
        ac = statics.actual_at_employment(f, xt["md"], xt["a"], xt["psi"], xt["rho"],
                                          l_C, l_N, dlnA)
        row.dlnY, row.dlnr, row.dlnK, row.s_L = ac.dlnY, ac.dlnr, ac.dlnK, ac.s_L
        row.dlnw_C_mpl = ac.dlnw_C_tilde + dlnA
        row.dlnw_N = ac.dlnw_N_tilde + dlnA
        # average wage of the employed, at the wages paid
        wC = math.exp(row.dlnw_C_paid)
        wN = math.exp(row.dlnw_N)
        row.dlnw_avg = math.log((wC * l_C + wN * l_N) / (l_C + l_N))
        row.u_excess = (U_C + U_N - f.U_bar) / f.L
        row.u_rate = (U_C + U_N) / f.L
        row.u_rate_C = U_C / (U_C + l_C)
        row.u_rate_N = U_N / (U_N + l_N)
        row.overhang = row.G_C * l_C / f.L
        row.cog_shift = math.log(fr.l_C_star / f.l_C0)

        # 9. Ideas: the uplift is the GDP gap; step forward on (42)
        row.dlnR = row.dlnY
        row.dg = f.g * (math.exp(f.lam * row.dlnR - f.fishing_out_R * dlnA) - 1.0)

        # 7. Stocks (done last so the row records start-of-month state)
        l_C_next = (1.0 - row.q_C) * l_C - row.D_C + row.H_C                 # (36)
        l_N_next = (1.0 - row.q_N) * l_N + row.H_N
        U_C_next = U_C + row.q_C * l_C + row.D_C - row.f_C * U_C             # (37)
        U_N_next = U_N + row.q_N * l_N - row.f_N * U_N
        row.reallocation = (abs(l_C_next - l_C) + abs(l_N_next - l_N)) / (2.0 * f.L)

        res.months.append(row)
        l_C, l_N, U_C, U_N = l_C_next, l_N_next, U_C_next, U_N_next
        f_C_lag, f_N_lag = row.f_C, row.f_N
        dlnA = dlnA + h * row.dg

    return res


def ideas_closed_form(res: Result, t: float) -> float:
    """Equation (43): the exact level effect, as a check on the monthly step."""
    f = res.fixed
    k = res.months.index(res.at(t))
    fo = f.fishing_out_R
    integral = 0.0
    for j in range(k + 1):                      # trapezoid on a monthly grid
        s = res.months[j].t
        w = f.h * (0.5 if j in (0, k) else 1.0)
        integral += w * math.exp(-fo * f.g * (t - s)) * math.exp(f.lam * res.months[j].dlnR)
    return math.log(math.exp(-fo * f.g * (t - f.t0)) + fo * f.g * integral) / fo
