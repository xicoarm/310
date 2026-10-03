#!/usr/bin/env python3
"""Back-of-the-envelope feasibility for a residential parcel in Widen AG.

Every input is a named assumption so it can be swapped for a quote, a BNO
value or a broker figure. Prices in CHF, areas in m², all excl. VAT effects
(residential construction in CH is VAT-exempt for the buyer of a finished
home, so costs below are gross).
"""
import json
import sys
from dataclasses import dataclass, asdict, field


@dataclass
class Site:
    land_m2: float
    az: float                     # Ausnützungsziffer from the BNO
    asking_price: float = 1_550_000
    attic_bonus: float = 0.30     # Attika/Dachgeschoss on top of aGF, if not counted in AZ
    existing_living_m2: float = 0  # rentable area of what stands there today
    existing_units: int = 0


@dataclass
class Market:
    land_price_m2: float = 1_090        # average Widen, immobilienindex.ch
    rent_existing_m2_yr: float = 270     # older stock, below the 293 average
    rent_new_m2_yr: float = 315          # new build, Mutschellen
    condo_price_new_m2: float = 9_500    # new-build condo, NWF
    house_price_m2: float = 8_500


@dataclass
class Costs:
    build_cost_hnf_m2: float = 5_200   # BKP 1-5 + 9, incl. fees, permits, parking; excl. land
    demolition_lump: float = 60_000
    opex_share: float = 0.18           # non-recoverable running costs + vacancy, % of gross rent
    capex_reserve_m2_yr: float = 20    # maintenance reserve on existing buildings
    sale_costs_share: float = 0.03     # broker/marketing on condo sales
    purchase_costs_share: float = 0.006  # 0.4 % Grundbuchabgabe + notary/fees
    hnf_ratio: float = 0.80            # usable living area / gross floor area
    mortgage_rate: float = 0.018       # 10y fixed, Oct 2026 range 1.5-2.1 %
    ltv: float = 0.65


def aargau_ggst_rate(years: float) -> float:
    """Grundstückgewinnsteuer rate for private sellers in Aargau."""
    if years < 1:
        return 0.40
    if years <= 11:
        return max(0.40 - 0.02 * int(years), 0.18)
    return max(0.18 - 0.01 * (int(years) - 11), 0.05)


def run(site: Site, market: Market = Market(), costs: Costs = Costs()):
    buy_all_in = site.asking_price * (1 + costs.purchase_costs_share)
    agf = site.az * site.land_m2
    gf_total = agf * (1 + site.attic_bonus)
    hnf = gf_total * costs.hnf_ratio
    out = {
        "inputs": {"site": asdict(site), "market": asdict(market), "costs": asdict(costs)},
        "potential": {"aGF_m2": round(agf), "GF_with_attic_m2": round(gf_total), "living_area_m2": round(hnf),
                      "units_at_95m2": round(hnf / 95, 1)},
        "price_check": {
            "asking_per_land_m2": round(site.asking_price / site.land_m2),
            "land_value_at_market": round(site.land_m2 * market.land_price_m2),
            "asking_per_buildable_m2": round(site.asking_price / max(hnf, 1)),
        },
    }

    # A. Hold & rent what stands there
    if site.existing_living_m2:
        rent = site.existing_living_m2 * market.rent_existing_m2_yr
        noi = rent * (1 - costs.opex_share) - site.existing_living_m2 * costs.capex_reserve_m2_yr
        out["A_hold_and_rent"] = {
            "gross_rent_yr": round(rent), "net_income_yr": round(noi),
            "gross_yield": round(rent / buy_all_in, 4), "net_yield": round(noi / buy_all_in, 4),
            "equity_cash_on_cash": round((noi - buy_all_in * costs.ltv * costs.mortgage_rate) / (buy_all_in * (1 - costs.ltv)), 4),
        }

    # B. Replace with new build, keep and rent
    build = hnf * costs.build_cost_hnf_m2 + (costs.demolition_lump if site.existing_living_m2 else 0)
    invest = buy_all_in + build
    rent_new = hnf * market.rent_new_m2_yr
    noi_new = rent_new * (1 - costs.opex_share)
    out["B_build_to_rent"] = {
        "build_cost": round(build), "total_investment": round(invest),
        "gross_rent_yr": round(rent_new), "net_income_yr": round(noi_new),
        "gross_yield_on_cost": round(rent_new / invest, 4), "net_yield_on_cost": round(noi_new / invest, 4),
        "value_at_3pct_net_cap": round(noi_new / 0.030), "value_minus_cost": round(noi_new / 0.030 - invest),
    }

    # C. Build condos and sell (private seller, ~3 years holding)
    revenue = hnf * market.condo_price_new_m2
    profit_pre_tax = revenue * (1 - costs.sale_costs_share) - invest - invest * 0.5 * costs.mortgage_rate * 2
    tax = max(profit_pre_tax, 0) * aargau_ggst_rate(3)
    out["C_build_to_sell"] = {
        "sales_revenue": round(revenue), "profit_before_tax": round(profit_pre_tax),
        "margin_on_cost": round(profit_pre_tax / invest, 4), "ggst_3y": round(tax),
        "profit_after_tax": round(profit_pre_tax - tax),
    }

    # Residual land value: what a developer could pay for the land
    target_margin = 0.12
    residual = (revenue * (1 - costs.sale_costs_share) / (1 + target_margin) - (build)) / (1 + costs.purchase_costs_share)
    out["residual_land_value_condo_12pct"] = round(residual)
    residual_rent = (noi_new / 0.032 - build) / (1 + costs.purchase_costs_share)
    out["residual_land_value_rental_3_2pct"] = round(residual_rent)
    return out


if __name__ == "__main__":
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"land_m2": 1000, "az": 0.45}
    print(json.dumps(run(Site(**args)), indent=1))
