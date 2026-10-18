"""Slow-accumulation model: monthly spend split between a sealed-hold sleeve (bought ~MSRP)
and a flip sleeve (collections/bulk/show buys recycled). Calibrated to PriceCharting/TCGinvest data
collected 2026-10-18. All assumptions printed with results."""

LEVELS = {  # monthly spend, sealed share, flip share (rest = supplies/tools/fees), weekly hours
    "L1 Hobbyist": (250, 0.70, 0.20, 3),
    "L2 Typical part-time": (900, 0.50, 0.42, 7),
    "L3 Serious part-time": (2500, 0.40, 0.55, 14),
}
# sealed market value per $ of cost after m months (cost includes ~8% tax, so start at 0.93 of cost)
SCEN = {
    "best": lambda m: 0.93 * (1 + 0.035 * m),          # ~2023-25 SV experience (+3.5%/mo linear)
    "base": lambda m: 0.93 * (1 + 0.010 * m),          # ~12%/yr
    "worst": lambda m: 0.93 * (1 - 0.015 * min(m, 12)),  # reprint/correction, -18% then flat
}
FLIP = {"best": (0.25, 4), "base": (0.12, 3), "worst": (0.03, 2)}  # net margin per turn, turns/yr
SELL_COST = 0.12  # haircut to liquidate sealed (fees/shipping or show discount)

for lvl, (spend, s_sh, f_sh, hrs) in LEVELS.items():
    print(f"\n{lvl}: ${spend}/mo  sealed {s_sh:.0%}  flip {f_sh:.0%}  ~{hrs} h/wk")
    for sc in ("best", "base", "worst"):
        out = []
        for horizon in (12, 24):
            sealed_mv = sum(spend * s_sh * SCEN[sc](horizon - k) for k in range(horizon))
            flip_cap = 0.0; flip_profit = 0.0
            mrg, turns = FLIP[sc]
            for k in range(horizon):
                flip_cap += spend * f_sh
                flip_profit += flip_cap * mrg * turns / 12
            invested = spend * horizon
            liq = sealed_mv * (1 - SELL_COST) + flip_cap + flip_profit
            out.append(f"m{horizon}: invested ${invested:,.0f} | sealed MV ${sealed_mv:,.0f} | flip capital ${flip_cap:,.0f} + profit ${flip_profit:,.0f} | liquidation ${liq:,.0f} ({(liq / invested - 1) * 100:+.0f}%)")
        print(f"  {sc:5}: " + "\n         ".join(out))
