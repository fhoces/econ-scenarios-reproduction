"""The monthly simulation: steps 1-9 of Appendix A (pp. 40-41) over the 44-equation
system of Table A.1.

One call to run() walks a scenario from the 2024 base period to 2030 one month at
a time. Within a month the equations are recursive (each step only needs what the
earlier steps produced), so the loop body below follows Appendix A's numbered
order, with step 7 (the stocks carried into next month) done last so that each
row records the start-of-month state. Only two steps need a root-find, and both
are one monotone equation in one unknown (statics.py).

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
    """One row of the simulated path: everything Table A.1 names, per month.

    Fields default to 0.0 only so a row can be created with just its date and
    filled in step by step; every field is written before the row is stored.
    Subscript C is the paper's "cognitive" group, N is all other occupations.
    Head counts (l, U, N_C, D, v, S, H) are shares of the labor force; rates
    (q, f) are per month; everything starting with dln is a log gap against the
    no-AI path.
    """

    t: float
    # exogenous paths (Equation (8)), looked up at t
    m: float = 0.0              # affected mass
    d: float = 0.0              # diffusion share
    a: float = 0.0              # log gain per instance
    psi: float = 0.0            # automation share
    # ideas block (panel A)
    dlnA: float = 0.0           # ideas stock gap, predetermined from last month's step 9
    dlnR: float = 0.0           # research uplift = the GDP gap, (22)
    dg: float = 0.0             # gap in the growth rate of ideas, (42)
    # frictionless / target economy (panel B): Proposition 1, starred in the paper
    dlnr_star: float = 0.0      # rental-rate gap clearing the capital market, (18)
    s_L_star: float = 0.0       # labor share at the targets, (14)
    dlnw_common: float = 0.0    # the one common wage of the frictionless economy, (16)
    dlnYL_star: float = 0.0     # output per worker, identity (5)
    ell_N_tilde: float = 0.0    # shift in demand for all-other labor, (15)
    l_C_star: float = 0.0       # employment target, cognitive, (13)
    l_N_star: float = 0.0       # employment target, all other, (13)
    dln_tfp: float = 0.0        # measured TFP gap, (45)
    # flows (panel C)
    l_C: float = 0.0            # employment at the start of the month
    l_N: float = 0.0
    U_C: float = 0.0            # unemployed of cognitive origin
    U_N: float = 0.0            # unemployed of all-other origin
    G_C: float = 0.0            # cognitive overhang: log excess of employment over next month's target, (28)
    B_N: float = 0.0            # all-other shortfall: log gap up to next month's target, (28)
    q_C: float = 0.0            # quit rate this month, rising with last month's job prospects, (27)
    q_N: float = 0.0
    N_C: float = 0.0            # attached cognitive force: employed plus the excess pool, (29)
    x_C: float = 0.0            # ln(w_C,t / w_t), the rigid cognitive discount, (30)
    dlnw_C_clear: float = 0.0   # wage that would employ all of N_C, from (39)
    l_C_demand: float = 0.0     # cognitive labor firms want at the sticky wage, (39)
    E: float = 0.0              # excess employment carried into the month, l_C - l^d_C if positive
    Z: float = 0.0              # cognitive shortfall, l^d_C - l_C if positive (usually zero)
    D_C: float = 0.0            # layoffs: the excess that quits do not remove, (31)
    v_C: float = 0.0            # job openings posted this month, (32)
    v_N: float = 0.0
    S_C: float = 0.0            # effective search directed at each group, (33)
    S_N: float = 0.0
    H_C: float = 0.0            # hires, from the matching function (34)
    H_N: float = 0.0
    f_C: float = 0.0            # job-finding rate of the unemployed by ORIGIN group, (35)
    f_N: float = 0.0
    # reporting (panel D), the actual economy at realized employment
    dlnY: float = 0.0           # the GDP gap, from (39)
    dlnw_C_paid: float = 0.0    # the sticky cognitive wage actually paid (Table 3 uses this)
    dlnw_C_mpl: float = 0.0     # the cognitive marginal product at realized employment
    dlnw_N: float = 0.0         # the all-other wage, from (39)
    dlnw_avg: float = 0.0       # employment-weighted average of the wages paid
    dlnr: float = 0.0           # rental-rate gap at realized employment
    dlnK: float = 0.0           # capital stock gap
    s_L: float = 0.0            # labor share of income
    u_excess: float = 0.0       # pool above its normal level, share of L (Table A.1, unnumbered)
    u_rate: float = 0.0         # unemployment rate, all workers
    u_rate_C: float = 0.0       # unemployment rate of the cognitive group (pool over pool plus employed)
    u_rate_N: float = 0.0
    reallocation: float = 0.0   # gross employment change this month, share of L (Table A.1, X_t)
    overhang: float = 0.0       # aggregate overhang, the cognitive overhang weighted by employment
    cog_shift: float = 0.0      # ln(l*_C / l_C,t0), the required cognitive shift, second line of (19)


@dataclass
class Result:
    """A simulated scenario: the inputs it was run with (parameters, scenario, fitted
    paths, steady state) and one Month row per month from t0 to t_end."""

    fixed: Fixed
    scen: Scenario
    paths: Paths
    ss: steady.SteadyState
    months: list = field(default_factory=list)

    def at(self, t: float) -> Month:
        """The row closest to date t (t must lie within the simulated path)."""
        if not self.months[0].t - 1e-6 <= t <= self.months[-1].t + 1e-6:
            raise ValueError(f"t = {t} is outside the simulated path "
                             f"[{self.months[0].t}, {self.months[-1].t}]")
        return min(self.months, key=lambda r: abs(r.t - t))

    def series(self, name: str) -> list:
        """One Month field as a list over the whole path, e.g. series("dlnY")."""
        return [getattr(r, name) for r in self.months]

    def growth(self, name: str, t: float, months: int = 12) -> float:
        """Log change in a gap-plus-trend series over the preceding `months`."""
        i = self.months.index(self.at(t))
        if i < months:
            raise ValueError(f"no {months}-month history before t = {t}")
        return getattr(self.months[i], name) - getattr(self.months[i - months], name)


def run(fixed: Fixed, scen: Scenario, t_end: float = 2030.0) -> Result:
    """Simulate one scenario from t0 to t_end on a monthly grid."""
    f, h = fixed, fixed.h
    p = Paths.build(f, scen)
    ss = steady.solve(f)               # normal times, at mu_bar in every scenario
    res = Result(fixed=f, scen=scen, paths=p, ss=ss)

    # Wage rigidity per month, Equation (30): xi is the fraction of the cognitive
    # discount's gap that survives a YEAR, so xi^(1/12) is the fraction that
    # survives one month (0.5 per year is 0.944 per month).
    xi_m = f.xi ** (1.0 / 12.0)
    # Equation (27) splits each group's normal quit rate q_bar into an exogenous
    # part qX (a fixed 45 percent of it) and a part qT (55 percent, Table 1's
    # "share of quits that responds to job prospects") that scales with last
    # month's job-finding rate relative to normal. In normal times qX + qT = q_bar.
    qX = {"C": (1.0 - f.q_resp_share) * ss.q_C, "N": (1.0 - f.q_resp_share) * ss.q_N}
    qT = {"C": f.q_resp_share * ss.q_C, "N": f.q_resp_share * ss.q_N}

    # State, predetermined at t0 (Table A.1 notes, p. 43): no ideas gap yet,
    # employment and the pools at the steady state, last month's finding rates at
    # their normal values, and no cognitive discount.
    dlnA = 0.0
    l_C, l_N = f.l_C0, f.l_N0
    U_C, U_N = ss.U_C, ss.U_N
    f_C_lag, f_N_lag = ss.f_C, ss.f_N
    x_C = 0.0                                  # w_C,t0-1 = w_t0-1

    n_months = int(round((t_end - f.t0) * 12)) + 1     # 73 months, 2024.0 to 2030.0 inclusive
    for k in range(n_months):
        t = f.t0 + k * h
        row = Month(t=t)

        # 1. Paths: a lookup, not a solve. The AI objects at t, and at t + 1 month
        # because step 3 needs next month's employment targets. m and d only ever
        # enter as their product, so at() also returns "md".
        xt = p.at(t)
        xt1 = p.at(t + h)
        row.m, row.d, row.a, row.psi = xt["m"], xt["d"], xt["a"], xt["psi"]
        row.dlnA = dlnA                        # carried in from step 9 of last month

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

        # 4. Gaps and the cognitive wage. On the scenario paths the cognitive target
        # only falls and the all-other target only rises, so the cognitive group
        # carries an overhang G_C and the other a shortfall B_N, both against NEXT
        # month's target (28), and both log gaps clipped at zero.
        row.l_C, row.l_N, row.U_C, row.U_N = l_C, l_N, U_C, U_N
        row.G_C = max(0.0, math.log(l_C) - math.log(l_C_star_next))          # (28)
        row.B_N = max(0.0, math.log(l_N_star_next) - math.log(l_N))          # (28)
        row.N_C = l_C + max(0.0, U_C - ss.U_C)                               # (29)
        # The wage that would employ the whole attached force N_C: system (39)
        # evaluated at (N_C, l_N) instead of realized employment.
        clear = statics.actual_at_employment(f, xt["md"], xt["a"], xt["psi"], xt["rho"],
                                            row.N_C, l_N, dlnA)              # w^c_C by (39)
        row.dlnw_C_clear = clear.dlnw_C_tilde + dlnA
        # (30): the discount to the common wage closes a fraction (1 - xi_m) of its
        # gap to the clearing discount each month. What is rigid is the discount,
        # not the wage level; both sides are A-deflated, and the deflator cancels.
        x_C = xi_m * x_C + (1.0 - xi_m) * (clear.dlnw_C_tilde - fr.dlnw_tilde)
        row.x_C = x_C
        wtC = fr.dlnw_tilde + x_C                                            # A-deflated
        row.dlnw_C_paid = wtC + dlnA
        # At that sticky wage firms want l^d_C: system (39) solved for l_C. The
        # difference from actual employment is either excess E (to be shed) or a
        # shortfall Z (to be hired), never both.
        l_C_d, _, _ = statics.cognitive_demand(f, xt["md"], xt["a"], xt["psi"], xt["rho"],
                                               wtC, l_N, dlnA)
        row.l_C_demand = l_C_d
        row.E = max(0.0, l_C - l_C_d)
        row.Z = max(0.0, l_C_d - l_C)

        # 5. Separations and openings. Quits rise with LAST month's finding rate
        # relative to normal (27). Quits from surplus positions are not replaced;
        # layoffs D_C remove whatever excess quits do not (31). Openings replace
        # the quits that are not surplus, plus a fraction theta_H of the shortfall,
        # all divided by the normal filling rate because only that fraction of a
        # posting is expected to fill within the month (32).
        row.q_C = qX["C"] + qT["C"] * f_C_lag / ss.f_C                       # (27)
        row.q_N = qX["N"] + qT["N"] * f_N_lag / ss.f_N
        row.D_C = max(0.0, row.E - row.q_C * l_C)                            # (31)
        row.v_C = (max(0.0, row.q_C * l_C - row.E) + scen.theta_H * row.Z) / ss.pi_C
        row.v_N = (row.q_N + scen.theta_H * row.B_N) * l_N / ss.pi_N         # (32)

        # 6. Matching. Searchers count fully in their origin group and mu-fold in
        # the other (33); the den Haan et al. matching function (34) turns search
        # and openings into hires, never more than either; the finding rate by
        # origin (35) adds a worker's chances in both groups.
        row.S_C, row.S_N = steady.effective_search(U_C, U_N, scen.mu)        # (33)
        iota = f.iota_match
        def hires(S: float, v: float) -> float:                              # (34)
            if S <= 0.0 or v <= 0.0:
                return 0.0
            return ss.chi * S * v / (S ** iota + v ** iota) ** (1.0 / iota)
        row.H_C, row.H_N = hires(row.S_C, row.v_C), hires(row.S_N, row.v_N)
        hC = row.H_C / row.S_C if row.S_C > 0 else 0.0       # hires per unit of search
        hN = row.H_N / row.S_N if row.S_N > 0 else 0.0
        row.f_C = hC + scen.mu * hN                                          # (35)
        row.f_N = scen.mu * hC + hN

        # 8. Reporting: the actual economy at realized employment, system (39) once
        # more, this time at (l_C, l_N) as they stand. Two cognitive wages come out
        # of this month: the marginal product at realized employment (what the
        # system returns) and the sticky wage actually paid (step 4); Table 3 uses
        # the paid one. The ideas term is added back to every deflated wage.
        ac = statics.actual_at_employment(f, xt["md"], xt["a"], xt["psi"], xt["rho"],
                                          l_C, l_N, dlnA)
        row.dlnY, row.dlnr, row.dlnK, row.s_L = ac.dlnY, ac.dlnr, ac.dlnK, ac.s_L
        row.dlnw_C_mpl = ac.dlnw_C_tilde + dlnA
        row.dlnw_N = ac.dlnw_N_tilde + dlnA
        # average wage of the employed, at the wages paid (Table A.1 note, p. 43)
        wC = math.exp(row.dlnw_C_paid)
        wN = math.exp(row.dlnw_N)
        row.dlnw_avg = math.log((wC * l_C + wN * l_N) / (l_C + l_N))
        row.u_excess = (U_C + U_N - f.U_bar) / f.L         # pool above its normal level
        row.u_rate = (U_C + U_N) / f.L
        row.u_rate_C = U_C / (U_C + l_C)                   # by origin group
        row.u_rate_N = U_N / (U_N + l_N)
        row.overhang = row.G_C * l_C / f.L
        row.cog_shift = math.log(fr.l_C_star / f.l_C0)      # second line of (19), exact

        # 9. Ideas: the research uplift is the GDP gap (22); the growth gap follows
        # by (42), and the ideas stock steps forward by one month of it (the Euler
        # step of Table A.1, checked against the closed form (43) in the tests).
        row.dlnR = row.dlnY
        row.dg = f.g * (math.exp(f.lam * row.dlnR - f.fishing_out_R * dlnA) - 1.0)

        # 7. Stocks (done last so the row records start-of-month state). Employment
        # loses quits and layoffs and gains hires (36); each pool gains those
        # separations and loses the workers who found jobs (37). A worker hired into
        # a group counts as that group's from then on.
        l_C_next = (1.0 - row.q_C) * l_C - row.D_C + row.H_C                 # (36)
        l_N_next = (1.0 - row.q_N) * l_N + row.H_N
        U_C_next = U_C + row.q_C * l_C + row.D_C - row.f_C * U_C             # (37)
        U_N_next = U_N + row.q_N * l_N - row.f_N * U_N
        # Gross reallocation: half the sum of absolute employment changes, so that a
        # worker moving from C to N counts once (Table A.1, X_t).
        row.reallocation = (abs(l_C_next - l_C) + abs(l_N_next - l_N)) / (2.0 * f.L)

        res.months.append(row)
        l_C, l_N, U_C, U_N = l_C_next, l_N_next, U_C_next, U_N_next
        f_C_lag, f_N_lag = row.f_C, row.f_N
        dlnA = dlnA + h * row.dg                   # the ideas stock carried into t + 1

    return res


def ideas_closed_form(res: Result, t: float) -> float:
    """Equation (43): the exact level effect, as a check on the monthly step.

    The integral in (43) runs over the simulated research uplift from t0 to t and
    is evaluated by the trapezoid rule on the monthly grid (half weight on the two
    end months). fo is 1 - phi_R, the fishing-out strength 2.86.
    """
    f = res.fixed
    k = res.months.index(res.at(t))
    fo = f.fishing_out_R
    integral = 0.0
    for j in range(k + 1):                      # trapezoid on a monthly grid
        s = res.months[j].t
        w = f.h * (0.5 if j in (0, k) else 1.0)
        integral += w * math.exp(-fo * f.g * (t - s)) * math.exp(f.lam * res.months[j].dlnR)
    return math.log(math.exp(-fo * f.g * (t - f.t0)) + fo * f.g * integral) / fo
