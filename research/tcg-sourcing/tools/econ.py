"""Unit economics for TCG sourcing -> outlet combos, using fee schedules verified 2026-10-18.
All figures USD. Income tax excluded. Sales tax collected by marketplaces is a pass-through
but eBay/TCGplayer/Whatnot compute some fees on tax-inclusive totals, which we model."""

TAX = 0.08  # buyer sales tax rate used where a fee is charged on tax-inclusive totals


def ebay(p, ship_cost):  # free shipping to buyer; FVF on total incl. tax (shipping charged = 0)
    fee = 0.1325 * p * (1 + TAX) + (0.40 if p > 10 else 0.30)
    return p - fee - ship_cost


def tcgplayer(p, ship_cost, ship_charged=0.0):  # Level 1-4 seller
    fee = 0.1075 * min(p, 75 / 0.1075) + 0.025 * (p + ship_charged) * (1 + TAX) + 0.30
    return p + ship_charged - fee - ship_cost


def whatnot(p, ship_cost=0.0):  # buyer pays shipping on Whatnot; processing on total incl. tax+ship
    buyer_ship = 0.0  # shipping is passed through, so ignore both sides
    fee = 0.08 * p + 0.029 * (p * (1 + TAX) + buyer_ship) + 0.30
    return p - fee - ship_cost


def mercari(p, ship_cost):
    return p - 0.10 * p - ship_cost


def show(p, card_share=0.5):  # Square 2.6% + 15c on card share; cash otherwise
    return p - card_share * (0.026 * p + 0.15)


def local(p):
    return p


SHIP_SEALED = 10.50   # USPS Ground Advantage ~2 lb + box/bubble, seller-paid, incl. insurance-ish buffer
SHIP_BOX = 14.00      # booster box, double-boxed


def row(label, cost, outs):
    print(f"\n{label}  (all-in cost ${cost:.2f})")
    for name, net in outs:
        prof = net - cost
        print(f"  {name:<34} net ${net:7.2f}  profit ${prof:7.2f}  margin {prof / cost * 100:6.1f}% of cost")


# Scenario A: ETB bought at retail MSRP ($49.99 + 8% tax), flipped in release window
cost = 49.99 * 1.08
for mkt in (65, 85, 130):
    row(f"A. ETB @MSRP -> market ${mkt}", cost, [
        ("eBay (free ship)", ebay(mkt, SHIP_SEALED)),
        ("TCGplayer L1-4 (free ship)", tcgplayer(mkt, SHIP_SEALED)),
        ("Whatnot auction @90% mkt", whatnot(mkt * 0.90)),
        ("Mercari (free ship)", mercari(mkt, SHIP_SEALED)),
        ("Card show @95% mkt, 50% card", show(mkt * 0.95)),
        ("FB local @95% mkt", local(mkt * 0.95)),
    ])

# Scenario B: ETB at distributor pre-order cost (~$33, reported) -- shows the value of access
row("B. ETB @distributor ~$33 -> market $85", 33.0, [
    ("eBay", ebay(85, SHIP_SEALED)), ("Card show @95%", show(85 * 0.95)), ("Sell to LGS/plug @MSRP 49.99", 49.99)])

# Scenario C: buy sealed on FB at 85% of market, resell (pure arbitrage)
for mkt in (85, 300):
    c = 0.85 * mkt
    row(f"C. Sealed bought @85% of ${mkt} market (FB/local)", c, [
        ("eBay (free ship)", ebay(mkt, SHIP_SEALED if mkt < 200 else SHIP_BOX)),
        ("TCGplayer", tcgplayer(mkt, SHIP_SEALED if mkt < 200 else SHIP_BOX)),
        ("Card show @95%", show(mkt * 0.95)),
        ("FB local @100%", local(mkt)),
    ])

# Scenario D: booster box at MSRP (LGS pre-order, $161.64 + tax) held, sold at various outcomes
cost = 161.64 * 1.08
for mkt in (150, 230, 300, 450):
    row(f"D. Booster box @MSRP held -> market ${mkt}", cost, [
        ("eBay", ebay(mkt, SHIP_BOX)), ("Card show @95%", show(mkt * 0.95)), ("FB local @97%", local(mkt * 0.97))])

# Scenario E: $1,000-market raw collection bought at 65%; 70% of value is listable singles, 30% bulk-ish
paid = 650.0
singles_val, bulk_val = 700.0, 300.0
n_singles = 60  # avg $11.67
# singles: TCGplayer, buyer pays $1.40 shipping on <$5? model avg: seller ship cost $1.00 PWE-ish (ESE ~0.74 + supplies)
tcg_singles = sum(tcgplayer(singles_val / n_singles, 1.10, ship_charged=1.40) for _ in range(n_singles))
show_singles = show(singles_val * 0.90)
bulk_out = bulk_val * 0.40  # bulk/low-end sold to bulk buyer or as lots
row("E. $1,000-market collection bought @65% ($650)", paid, [
    ("Singles on TCGplayer + bulk @40%", tcg_singles + bulk_out),
    ("Singles at show @90% + bulk @40%", show_singles + bulk_out),
    ("Flip whole lot to vendor @75%", 750.0),
])

# Scenario F: show-level P&L for a first local table
print("\nF. First local show P&L (table $135, gas/food $40, 6-8 hrs)")
for gross, cogs_ratio in ((650, 0.80), (1500, 0.78), (3000, 0.80)):
    proc = 0.5 * (0.026 * gross) + 0.15 * (gross / 40)  # half on card, ~$40 avg ticket
    profit = gross - gross * cogs_ratio - proc - 135 - 40
    print(f"  gross ${gross:5}: COGS {cogs_ratio:.0%} -> net ${profit:7.2f}")
