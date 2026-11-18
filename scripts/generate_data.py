"""
Synthetic data generator for the Sales Velocity Dashboard.

Produces one CSV per Power BI model table (same table and column names as the
original mart layer) with ~2 years of multi-channel e-commerce data:
- mega-sale days (1.1 ... 12.12), payday sales (15th, 25th), Tet, year-end season
- channel growth (TikTok Shop ramps up), weekend effect
- cancellations, late-arriving returns, orders still in progress near "today"
- combos (bundles) that are exploded into component SKUs for demand
- daily inventory snapshots with restocking, days of cover and negative stock

All names and numbers are fictional.

Usage:
    python scripts/generate_data.py          # writes CSVs to ./data
"""

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 7
START = date(2025, 1, 1)
END = date(2026, 11, 15)               # the dataset's "today"
BASE_ORDERS_PER_DAY = 220
OUT_DIR = Path(__file__).resolve().parent.parent / "data"
LOADED_AT = pd.Timestamp(END) + pd.Timedelta(hours=6)

rng = np.random.default_rng(SEED)


def dkey(s):
    """date-like Series -> yyyymmdd integer key (nullable)."""
    s = pd.to_datetime(s)
    return (s.dt.year * 10000 + s.dt.month * 100 + s.dt.day).astype("Int64")


# =============================================================================
# Dimensions
# =============================================================================
# ---- warehouses --------------------------------------------------------------
dim_warehouse = pd.DataFrame({
    "warehouse_key": [1, 2, 3],
    "depot_id": [5101, 5102, 5199],
    "depot_code": ["WH-HCM", "WH-HN", "WH-RTN"],
    "depot_name": ["Main Warehouse HCM", "Warehouse Ha Noi", "Returns & Damaged"],
    "city_name": ["Ho Chi Minh", "Ha Noi", "Ho Chi Minh"],
    "is_sellable_depot": [True, True, False],
})

# ---- shops --------------------------------------------------------------------
# key, channel_code, channel, marketplace, shop_id, label, name, brand, region,
# base_weight, growth/yr, cancel_rate, return_rate, platform_fee_rate, warehouse_key
SHOP_ROWS = [
    (1, 20, "Shopee", True, "SP_10001", "SHOPEE LUMI HCM", "Lumi Store HCM", "Lumi", "South", 0.42, 0.08, 0.110, 0.020, 0.16, 1),
    (2, 20, "Shopee", True, "SP_10002", "SHOPEE LUMI HN", "Lumi Store HN", "Lumi", "North", 0.27, 0.15, 0.100, 0.018, 0.16, 2),
    (3, 20, "Shopee", True, "SP_10003", "SHOPEE VELVET MALL", "Velvet Beauty Mall", "Velvet", "South", 0.02, 0.60, 0.095, 0.015, 0.20, 1),
    (4, 30, "TikTok Shop", True, "TT_20001", "TIKTOK LUMI", "Lumi Official", "Lumi", "South", 0.17, 0.90, 0.125, 0.025, 0.13, 1),
    (5, 30, "TikTok Shop", True, "TT_20002", "TIKTOK VELVET", "Velvet Beauty", "Velvet", "South", 0.015, 0.30, 0.140, 0.030, 0.13, 1),
    (6, 40, "Lazada", True, "LZ_30001", "LAZADA LUMI", "Lumi Store", "Lumi", "South", 0.05, -0.15, 0.120, 0.022, 0.15, 1),
    (7, 10, "Internal (Admin)", False, "ADMIN", "ADMIN (INTERNAL)", "Admin / B2B", "Lumi", "South", 0.006, 0.20, 0.040, 0.005, 0.00, 1),
]
shops = pd.DataFrame(SHOP_ROWS, columns=[
    "shop_key", "sale_channel_code", "sale_channel_name", "is_marketplace", "shop_id", "shop_label",
    "platform_shop_name", "brand", "region", "w", "growth", "cancel", "ret", "fee", "wh"])
shops["shop_name"] = shops.shop_label

# ---- products -----------------------------------------------------------------
CATS = [
    # vi name, en name, nhanh_category_id, n_skus, min_price, max_price, popularity
    ("Lô cuốn tóc", "Hair Rollers", 101, 8, 25_000, 89_000, 0.18),
    ("Mút trang điểm", "Makeup Sponges", 102, 8, 19_000, 69_000, 0.15),
    ("Bộ cọ trang điểm", "Makeup Brush Sets", 103, 5, 129_000, 399_000, 0.08),
    ("Cọ mắt", "Eye Makeup Brushes", 104, 7, 29_000, 99_000, 0.10),
    ("Cọ nền", "Foundation Brushes", 105, 5, 49_000, 149_000, 0.07),
    ("Lược", "Combs & Hairbrushes", 106, 6, 29_000, 159_000, 0.10),
    ("Nhíp, kéo, dao cạo", "Razors, Tweezers & Scissors", 107, 6, 25_000, 119_000, 0.10),
    ("Phụ kiện phòng tắm", "Bathroom Accessories", 108, 7, 35_000, 189_000, 0.12),
    ("Sản phẩm hỗ trợ", "Supporting Products", 109, 5, 15_000, 59_000, 0.06),
    ("Quà tặng", "Gifts", 110, 4, 0, 0, 0.0),
]
prod_rows = []
pk = 1
for vi, en, cat_id, n, lo, hi, pop in CATS:
    for i in range(n):
        price = 0 if en == "Gifts" else int(round(rng.uniform(lo, hi), -3))
        prod_rows.append(dict(
            product_key=pk, product_id=900000 + pk, sku_code=f"LM-{cat_id}-{i + 1:02d}",
            product_name=f"{en} {i + 1:02d}" if en != "Gifts" else f"Free Gift {i + 1:02d}",
            product_type_code=1, is_combo=False, is_test_product=False,
            category_name=vi, category_name_en=en, nhanh_category_id=cat_id, nhanh_category_name=vi,
            retail_price=price, weight=pop / n if pop else 0.0, is_gift=(en == "Gifts")))
        pk += 1

singles = pd.DataFrame(prod_rows)
sellable = singles[~singles.is_gift].reset_index(drop=True)

# combos: 2-3 components, priced ~12% below the sum of parts
COMBOS = {}
combo_rows = []
for i in range(8):
    comp_idx = rng.choice(len(sellable), size=rng.integers(2, 4), replace=False)
    comps = [(int(sellable.product_key[j]), int(rng.choice([1, 1, 2]))) for j in comp_idx]
    price = int(round(sum(sellable.set_index("product_key").retail_price[k] * q for k, q in comps) * 0.88, -3))
    first = sellable.set_index("product_key").loc[comps[0][0]]
    COMBOS[pk] = comps
    combo_rows.append(dict(
        product_key=pk, product_id=900000 + pk, sku_code=f"LM-CB-{i + 1:02d}", product_name=f"Combo {i + 1:02d}",
        product_type_code=2, is_combo=True, is_test_product=False,
        category_name=first.category_name, category_name_en=first.category_name_en,
        nhanh_category_id=first.nhanh_category_id, nhanh_category_name=first.nhanh_category_name,
        retail_price=price, weight=0.012, is_gift=False))
    pk += 1

extra_rows = [
    dict(product_key=pk, product_id=900000 + pk, sku_code="LM-TEST-01", product_name="Test product (do not sell)",
         product_type_code=1, is_combo=False, is_test_product=True, category_name="Khác", category_name_en="Other",
         nhanh_category_id=199, nhanh_category_name="Khác", retail_price=1_000, weight=0.0, is_gift=False),
    dict(product_key=pk + 1, product_id=900001 + pk, sku_code="LM-PKG-01", product_name="Packaging bag (internal)",
         product_type_code=1, is_combo=False, is_test_product=False, category_name="Vật tư", category_name_en="Supplies",
         nhanh_category_id=198, nhanh_category_name="Vật tư", retail_price=0, weight=0.0, is_gift=False),
]
TEST_PK = pk
products = pd.concat([singles, pd.DataFrame(combo_rows), pd.DataFrame(extra_rows)], ignore_index=True)
products["is_internal_item"] = products.sku_code.eq("LM-PKG-01")
products["is_category_mapped"] = ~products.category_name_en.isin(["Other", "Supplies"])
products["brand_id"] = 1
products["brand_name"] = "Lumi"
products["created_date"] = [START - timedelta(days=int(d)) for d in rng.integers(30, 900, len(products))]
products["attributes_as_of_date"] = END

# =============================================================================
# Daily demand curve
# =============================================================================
TET = {2025: date(2025, 1, 29), 2026: date(2026, 2, 17)}


def day_multiplier(d: date) -> float:
    m = 1.0
    nxt = d + timedelta(days=1)
    if d.day == d.month:
        m *= 3.2 if d.month in (9, 10, 11, 12) else 2.5
    elif d.day in (15, 25):
        m *= 1.5
    elif nxt.day == nxt.month:
        m *= 1.15
    if d.weekday() >= 5:
        m *= 1.08
    if d.month in (11, 12):
        m *= 1.15
    tet = TET.get(d.year)
    if tet:
        delta = (d - tet).days
        if -21 <= delta <= -8:
            m *= 1.35
        elif -7 <= delta <= -1:
            m *= 0.75
        elif 0 <= delta <= 5:
            m *= 0.35
        elif 6 <= delta <= 12:
            m *= 0.8
    return m


days = pd.date_range(START, END, freq="D")
t_day = (days - pd.Timestamp(START)).days / 365.0
expected = (BASE_ORDERS_PER_DAY * (1 + 0.18 * t_day)
            * np.array([day_multiplier(d.date()) for d in days])
            * rng.normal(1, 0.08, len(days)).clip(0.75, 1.3))
orders_per_day = rng.poisson(expected)

# =============================================================================
# Orders (header)
# =============================================================================
n = int(orders_per_day.sum())
o_day = pd.to_datetime(np.repeat(days.values, orders_per_day))
t_years = ((o_day - pd.Timestamp(START)).days / 365.0).to_numpy()

w = shops.w.to_numpy()[None, :] * (1 + shops.growth.to_numpy()[None, :] * t_years[:, None])
w = np.clip(w, 1e-4, None)
w /= w.sum(axis=1, keepdims=True)
s_idx = (rng.random(n)[:, None] > w.cumsum(axis=1)).sum(axis=1)

hour_w = np.array([2, 1, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 6, 5, 5, 5, 5, 5, 6, 7, 8, 9, 8, 5], float)
created_at = (o_day + pd.to_timedelta(rng.choice(24, n, p=hour_w / hour_w.sum()), unit="h")
              + pd.to_timedelta(rng.integers(0, 3600, n), unit="s"))
order_ix = np.argsort(created_at.values, kind="stable")
created_at = created_at[order_ix]
s_idx = s_idx[order_ix]

o = pd.DataFrame({"order_id": np.arange(300_000_001, 300_000_001 + n), "created_at": created_at})
sh = shops.iloc[s_idx].reset_index(drop=True)
o["shop_key"] = sh.shop_key.values
o["warehouse_key"] = sh.wh.values
o["sale_channel_code"] = sh.sale_channel_code.values
o["sale_channel_name"] = sh.sale_channel_name.values
o["is_marketplace"] = sh.is_marketplace.values
o["shop_id"] = sh.shop_id.values
o["created_date"] = o.created_at.dt.normalize()
o["created_hour"] = o.created_at.dt.hour
age = (pd.Timestamp(END) - o.created_date).dt.days.to_numpy()

# status
u = rng.random(n)
status = np.where(u < sh.cancel.values, "Cancelled", "Delivered").astype(object)
returned = (status == "Delivered") & (rng.random(n) < sh.ret.values * np.clip((age - 3) / 18, 0, 1))
status[returned] = "Returned"
deliver_days = rng.choice([1, 2, 3, 4, 5], n, p=[0.15, 0.35, 0.3, 0.15, 0.05])
in_progress = (status == "Delivered") & (age < deliver_days + 1)
status[in_progress] = np.where(age[in_progress] <= 0, "Confirmed", "Shipping")
o["is_test_order"] = rng.random(n) < 0.002
STATUS = {  # name -> (status_code, status_group, order_status_key)
    "Confirmed": (42, "Processing", 2), "Shipping": (54, "Processing", 3),
    "Delivered": (60, "Success", 4), "Returned": (72, "Returned", 5), "Cancelled": (63, "Cancelled", 6),
}
o["status_name"] = status
o["status_code"] = o.status_name.map(lambda s: STATUS[s][0])
o["status_group"] = o.status_name.map(lambda s: STATUS[s][1])
o["order_status_key"] = o.status_name.map(lambda s: STATUS[s][2])
o["is_cancelled"] = o.status_name.eq("Cancelled")
o["is_returned"] = o.status_name.eq("Returned")
o["is_demand"] = ~o.is_test_order
o["is_revenue"] = o.status_name.eq("Delivered") & ~o.is_test_order

# =============================================================================
# Order lines
# =============================================================================
buyable = products[(products.weight > 0)].reset_index(drop=True)
n_lines = rng.choice([1, 2, 3, 4], n, p=[0.62, 0.25, 0.09, 0.04])
li_order = np.repeat(np.arange(n), n_lines)
li_prod = rng.choice(len(buyable), len(li_order), p=buyable.weight / buyable.weight.sum())
lines = pd.DataFrame({
    "oi": li_order,
    "product_key": buyable.product_key.values[li_prod],
    "qty": rng.choice([1, 2, 3, 5], len(li_order), p=[0.72, 0.19, 0.06, 0.03]),
    "retail_price": buyable.retail_price.values[li_prod],
    "is_free_item": False,
}).drop_duplicates(["oi", "product_key"])

gifts = singles[singles.is_gift]
g_orders = np.flatnonzero(rng.random(n) < 0.25)
gift_lines = pd.DataFrame({
    "oi": g_orders, "product_key": gifts.product_key.values[rng.integers(0, len(gifts), len(g_orders))],
    "qty": 1, "retail_price": 0, "is_free_item": True})
test_orders = np.flatnonzero(o.is_test_order.values)
lines = lines[~lines.oi.isin(test_orders)]
test_lines = pd.DataFrame({"oi": test_orders, "product_key": TEST_PK, "qty": 1, "retail_price": 1_000,
                           "is_free_item": False})
lines = pd.concat([lines, gift_lines, test_lines], ignore_index=True).sort_values(["oi", "is_free_item"])
lines["line_no"] = lines.groupby("oi").cumcount() + 1

promo = rng.choice([0, 0.05, 0.10, 0.15, 0.20], len(lines), p=[0.40, 0.20, 0.20, 0.12, 0.08])
lines["unit_price"] = (lines.retail_price * (1 - promo)).round(-3)
lines["line_subtotal"] = lines.qty * lines.retail_price
lines["line_total_amount"] = (lines.qty * lines.unit_price).astype(int)
lines["line_discount_amount"] = lines.line_subtotal - lines.line_total_amount
lines["is_combo"] = lines.product_key.isin(COMBOS.keys())

# order-level totals
pmap = products.set_index("product_key")
units_per_pk = {k: sum(q for _, q in v) for k, v in COMBOS.items()}
lines["_units"] = lines.qty * lines.product_key.map(units_per_pk).fillna(1).astype(int)
agg = lines.groupby("oi").agg(
    line_count=("line_no", "size"), sku_count=("product_key", "nunique"), qty_total=("qty", "sum"),
    qty_unit_total=("_units", "sum"), has_combo=("is_combo", "any"), has_free_item=("is_free_item", "any"),
    gross_amount=("line_subtotal", "sum"), line_discount_amount=("line_discount_amount", "sum"),
    lines_total_amount=("line_total_amount", "sum"))
o = o.join(agg, how="left")
o["has_test_product"] = o.is_test_order

voucher = rng.choice([0, 0, 0, 10_000, 15_000, 20_000, 30_000], n)
o["order_discount_amount"] = np.minimum(voucher, (o.lines_total_amount * 0.15).round(-3)).astype(int)
base = o.lines_total_amount - o.order_discount_amount
fee_missing = o.is_marketplace & (age < 10) & (rng.random(n) < 0.3)
o["platform_fee_amount"] = np.where(fee_missing, 0, (base * sh.fee.values).round(-2)).astype(int)
o["is_platform_fee_missing"] = fee_missing
o["net_received_amount"] = (base - o.platform_fee_amount).astype(int)
o["customer_ship_fee_amount"] = np.where(base >= 150_000, 0, rng.choice([15_000, 20_000, 25_000], n))
o["ship_fee_amount"] = rng.choice([18_000, 22_000, 25_000, 30_000], n)
# like the order management system: marketplace orders record the full amount the
# platform will pay out as COD; internal orders are COD only when paid on delivery
cod = o.is_marketplace.to_numpy() | (rng.random(n) < 0.2)
to_pay = base + o.customer_ship_fee_amount
o["cod_amount"] = np.where(cod, to_pay, 0).astype(int)
o["transfer_amount"] = np.where(cod, 0, to_pay).astype(int)
o["is_negative_payment"] = False

# timestamps
h_conf = rng.gamma(1.5, 1.5, n).round(2)
h_ship = rng.gamma(2.5, 5, n).round(2)
h_dlv = (deliver_days * 24 + rng.normal(0, 6, n)).clip(12).round(2)
early_cancel = o.is_cancelled & (rng.random(n) < 0.6)
o["confirmed_at"] = o.created_at + pd.to_timedelta(np.where(early_cancel, np.nan, h_conf), unit="h")
shipped = ~o.is_cancelled & ~o.status_name.eq("Confirmed")
o["packed_at"] = o.confirmed_at + pd.to_timedelta(np.where(shipped, h_ship * 0.6, np.nan), unit="h")
o["sent_to_carrier_at"] = o.confirmed_at + pd.to_timedelta(np.where(shipped, h_ship, np.nan), unit="h")
delivered = o.status_name.isin(["Delivered", "Returned"])
o["delivered_at"] = o.sent_to_carrier_at + pd.to_timedelta(np.where(delivered, h_dlv, np.nan), unit="h")
o.loc[o.delivered_at > LOADED_AT, ["delivered_at"]] = pd.NaT
o["delivered_date"] = o.delivered_at.dt.normalize()
o["hours_to_confirm"] = np.where(o.confirmed_at.notna(), h_conf, np.nan)
o["hours_to_ship"] = np.where(o.sent_to_carrier_at.notna(), h_ship, np.nan)
o["hours_to_deliver"] = np.where(o.delivered_at.notna(), h_dlv, np.nan)
o["is_time_anomaly"] = rng.random(n) < 0.001
o["updated_at"] = o[["created_at", "confirmed_at", "sent_to_carrier_at", "delivered_at"]].max(axis=1)

# other attributes
CARRIERS = {20: ["SPX Express", "J&T Express", "GHN"], 30: ["J&T Express", "GHN"],
            40: ["LEX", "GHN"], 10: ["GHN", "Viettel Post"]}
CARRIER_ID = {"SPX Express": 1, "J&T Express": 2, "GHN": 3, "LEX": 4, "Viettel Post": 5}
o["carrier_name"] = [CARRIERS[c][i % len(CARRIERS[c])] for c, i in
                     zip(o.sale_channel_code, rng.integers(0, 6, n))]
o["carrier_id"] = o.carrier_name.map(CARRIER_ID)
o["carrier_service_type_code"] = rng.choice([1, 2], n, p=[0.85, 0.15])
o["city_id"] = rng.choice([1, 2, 3, 4, 5, 6, 7, 8], n, p=[0.30, 0.22, 0.08, 0.07, 0.05, 0.05, 0.05, 0.18])
o["district_id"] = o.city_id * 100 + rng.integers(1, 20, n)
o["depot_id"] = o.warehouse_key.map(dim_warehouse.set_index("warehouse_key").depot_id)
o["order_type_code"] = 1
o["reason_code"] = np.where(o.is_cancelled, rng.choice([1, 2, 3, 4], n), np.nan)
o["original_order_id"] = np.nan
o["marketplace_order_id"] = np.where(
    o.is_marketplace, [f"{d:%y%m%d}{x:08X}" for d, x in zip(o.created_at, rng.integers(0, 2**32, n))], "")
o["created_date_key"] = dkey(o.created_date)
o["delivered_date_key"] = dkey(o.delivered_date)
o["_loaded_at"] = LOADED_AT

# allocate order discount and platform fee to lines (by line amount)
lines = lines.join(o[["order_id", "shop_key", "warehouse_key", "order_status_key", "created_date_key",
                      "delivered_date_key", "created_date", "delivered_date", "status_code", "status_group",
                      "is_demand", "is_revenue", "sale_channel_code", "order_discount_amount",
                      "platform_fee_amount", "lines_total_amount"]], on="oi")
share = np.where(lines.lines_total_amount > 0, lines.line_total_amount / lines.lines_total_amount, 0)
lines["_order_disc_alloc"] = (lines.order_discount_amount * share).round()
lines["platform_fee_alloc_amount"] = (lines.platform_fee_amount * share).round().astype(int)
lines["net_received_amount"] = (lines.line_total_amount - lines._order_disc_alloc
                                - lines.platform_fee_alloc_amount).astype(int)
lines["product_id"] = lines.product_key.map(pmap.product_id)
lines = lines.sort_values(["order_id", "line_no"]).reset_index(drop=True)
lines["order_line_id"] = np.arange(1, len(lines) + 1)
lines["_loaded_at"] = LOADED_AT

# =============================================================================
# mart_sales_daily  (demand by created date, revenue by delivered date)
# =============================================================================
K = ["shop_key", "product_key", "warehouse_key"]
dem = lines[lines.is_demand].assign(
    date_key=lambda d: d.created_date_key,
    _canc=lambda d: np.where(d.status_group == "Cancelled", d.qty, 0),
    _ret=lambda d: np.where(d.status_group == "Returned", d.qty, 0),
    _rev_created=lambda d: np.where(d.is_revenue, d.line_total_amount - d._order_disc_alloc, 0),
).groupby(["date_key"] + K).agg(
    qty_demand=("qty", "sum"), demand_amount=("line_total_amount", "sum"), qty_cancelled=("_canc", "sum"),
    qty_returned=("_ret", "sum"), revenue_by_created_amount=("_rev_created", "sum"),
    demand_line_count=("qty", "size"))
rev = lines[lines.is_revenue & lines.delivered_date_key.notna()].assign(
    date_key=lambda d: d.delivered_date_key,
    _disc=lambda d: d.line_discount_amount + d._order_disc_alloc,
    _rev=lambda d: d.line_total_amount - d._order_disc_alloc,
).groupby(["date_key"] + K).agg(
    qty_revenue=("qty", "sum"), revenue_gross_amount=("line_subtotal", "sum"),
    revenue_discount_amount=("_disc", "sum"), revenue_amount=("_rev", "sum"),
    platform_fee_amount=("platform_fee_alloc_amount", "sum"), net_received_amount=("net_received_amount", "sum"),
    revenue_line_count=("qty", "size"))
sales_daily = dem.join(rev, how="outer").fillna(0).reset_index()
for c in sales_daily.columns:
    if c not in ("revenue_gross_amount", "revenue_discount_amount"):
        sales_daily[c] = sales_daily[c].astype(int)
sales_daily["_loaded_at"] = LOADED_AT

# =============================================================================
# mart_sku_demand_daily  (combos exploded into component SKUs)
# =============================================================================
comp = pd.DataFrame([(c, k, q) for c, v in COMBOS.items() for k, q in v],
                    columns=["product_key", "comp_key", "comp_qty"])


def explode(df):
    direct = df[~df.is_combo].assign(unit=df.qty, from_combo=0)
    cmb = df[df.is_combo].merge(comp, on="product_key")
    cmb = cmb.assign(product_key=cmb.comp_key, unit=cmb.qty * cmb.comp_qty, from_combo=cmb.qty * cmb.comp_qty)
    return pd.concat([direct, cmb], ignore_index=True)


d_exp = explode(lines[lines.is_demand]).assign(date_key=lambda d: d.created_date_key)
d_agg = d_exp.groupby(["date_key"] + K).agg(qty_demand_unit=("unit", "sum"),
                                            qty_demand_unit_from_combo=("from_combo", "sum"))
r_exp = explode(lines[lines.is_revenue & lines.delivered_date_key.notna()]).assign(
    date_key=lambda d: d.delivered_date_key)
r_agg = r_exp.groupby(["date_key"] + K).agg(qty_revenue_unit=("unit", "sum"))
sku_daily = d_agg.join(r_agg, how="outer").fillna(0).astype(int).reset_index()
sku_daily["_loaded_at"] = LOADED_AT

# =============================================================================
# mart_inventory_daily  (simple stock simulation with restocking)
# =============================================================================
date_keys = dkey(pd.Series(days)).astype(int).to_numpy()
stock_items = products[~products.is_combo & ~products.is_test_product & ~products.is_internal_item].product_key.values
inv_frames = []
for wh in (1, 2):
    dem_wh = (d_exp[(d_exp.warehouse_key == wh) & (d_exp.status_group != "Cancelled")]
              .groupby(["date_key", "product_key"]).unit.sum()
              .unstack(fill_value=0).reindex(index=date_keys, columns=stock_items, fill_value=0))
    D = dem_wh.to_numpy(float)
    avg = np.maximum(D[:60].mean(axis=0), 0.3)
    stock = np.ceil(avg * rng.uniform(25, 50, len(stock_items)))
    pending = {}
    on_order = np.zeros(len(stock_items))
    remain = np.zeros_like(D)
    for t in range(len(date_keys)):
        arrived = pending.pop(t, 0)
        stock += arrived
        on_order -= arrived
        stock -= D[t]
        remain[t] = stock
        recent = D[max(0, t - 29):t + 1].mean(axis=0) + 0.05
        # reorder point ~ lead time + safety stock, counting stock already on order
        reorder = (stock + on_order) < recent * rng.uniform(12, 18, len(stock_items))
        if reorder.any():
            lead = int(rng.integers(7, 21))
            qty = np.where(reorder, np.ceil(recent * rng.uniform(25, 40, len(stock_items))), 0)
            pending[t + lead] = pending.get(t + lead, 0) + qty
            on_order += qty
    holding = np.floor(D * rng.uniform(0.2, 0.5, D.shape))
    shipping = np.floor(D * rng.uniform(0.5, 1.2, D.shape))
    transferring = np.where(rng.random(D.shape) < 0.02, rng.integers(5, 40, D.shape), 0)
    damaged = np.floor(np.maximum(remain, 0) * rng.choice([0, 0, 0, 0.01, 0.02], D.shape))
    available = remain - holding - damaged
    d30 = pd.DataFrame(D).rolling(30, min_periods=1).sum().to_numpy()
    f = pd.DataFrame({
        "date_key": np.repeat(date_keys, len(stock_items)),
        "product_key": np.tile(stock_items, len(date_keys)),
        "remain_qty": remain.ravel(), "holding_qty": holding.ravel(), "shipping_qty": shipping.ravel(),
        "transferring_qty": transferring.ravel(), "damaged_qty": damaged.ravel(),
        "available_qty": available.ravel(), "qty_demand_unit_30d": d30.ravel(),
    })
    f["warehouse_key"] = wh
    f["is_combo_derived"] = False
    inv_frames.append(f)

    # combo availability = min over components of (component available // qty per combo)
    avail = f.set_index(["date_key", "product_key"]).available_qty
    for ck, comps in COMBOS.items():
        parts = [np.floor(avail.xs(k, level="product_key").clip(lower=0) / q) for k, q in comps]
        c_av = pd.concat(parts, axis=1).min(axis=1)
        inv_frames.append(pd.DataFrame({
            "date_key": c_av.index, "product_key": ck, "remain_qty": c_av.values, "holding_qty": 0,
            "shipping_qty": 0, "transferring_qty": 0, "damaged_qty": 0, "available_qty": c_av.values,
            "qty_demand_unit_30d": 0, "warehouse_key": wh, "is_combo_derived": True}))

inv = pd.concat(inv_frames, ignore_index=True)
num = ["remain_qty", "holding_qty", "shipping_qty", "transferring_qty", "damaged_qty", "available_qty",
       "qty_demand_unit_30d"]
inv[num] = inv[num].astype(int)
inv["snapshot_date"] = pd.to_datetime(inv.date_key.astype(str), format="%Y%m%d").dt.date
inv["depot_id"] = inv.warehouse_key.map(dim_warehouse.set_index("warehouse_key").depot_id)
inv["is_sellable_depot"] = True
inv["is_negative_stock"] = inv.available_qty < 0
daily_rate = inv.qty_demand_unit_30d / 30
inv["days_of_cover"] = np.where(daily_rate > 0, (inv.available_qty.clip(lower=0) / daily_rate).round(1), np.nan)
inv["_loaded_at"] = LOADED_AT

# =============================================================================
# Finish dimensions (dates of first / last order)
# =============================================================================
first_last = lines[lines.is_demand].groupby("product_key").created_date.agg(["min", "max"])
products = products.join(first_last, on="product_key")
products["first_order_date"] = products["min"].dt.date
products["last_order_date"] = products["max"].dt.date
products["days_since_last_order"] = (pd.Timestamp(END) - products["max"]).dt.days.astype("Int64")
products["is_active"] = products.days_since_last_order.fillna(9999) <= 90
products["product_status"] = np.where(products.is_active, "Còn bán", "Ngừng bán")
# a few recently launched SKUs
new_sku = products.sku_code.isin(["LM-101-08", "LM-102-08", "LM-108-07"])
products.loc[new_sku, "product_status"] = "Mới"

fl = o.groupby("shop_key").created_date.agg(["min", "max"])
shops = shops.join(fl, on="shop_key")
shops["first_order_date"] = shops["min"].dt.date
shops["last_order_date"] = shops["max"].dt.date
shops["days_since_last_order"] = (pd.Timestamp(END) - shops["max"]).dt.days
shops["is_shop_active"] = shops.days_since_last_order <= 30
shops["is_shop_named"] = True

dd = pd.Series(days)
dim_date = pd.DataFrame({
    "date_key": dkey(dd).astype(int), "date_day": dd.dt.date, "year_num": dd.dt.year,
    "quarter_num": dd.dt.quarter, "month_num": dd.dt.month, "year_month": dd.dt.strftime("%Y-%m"),
    "iso_week_num": dd.dt.isocalendar().week.astype(int).values,
    "iso_week_year": dd.dt.isocalendar().year.astype(int).values,
    "day_of_week_num": dd.dt.weekday + 1, "day_of_month_num": dd.dt.day, "is_weekend": dd.dt.weekday >= 5,
    "month_start_date": dd.dt.to_period("M").dt.start_time.dt.date,
    "same_day_last_year_date": (dd - pd.DateOffset(years=1)).dt.date,
})

# =============================================================================
# Write CSVs (column order = Power BI model)
# =============================================================================
COLS = {
    "mart_dim_date": list(dim_date.columns),
    "mart_dim_shop": ["shop_key", "sale_channel_code", "sale_channel_name", "is_marketplace", "shop_id",
                      "shop_label", "shop_name", "platform_shop_name", "brand", "region", "is_shop_active",
                      "is_shop_named", "first_order_date", "last_order_date", "days_since_last_order"],
    "mart_dim_product": ["product_key", "product_id", "sku_code", "product_name", "product_type_code", "is_combo",
                         "is_test_product", "category_name", "brand_id", "brand_name", "retail_price",
                         "created_date", "attributes_as_of_date", "category_name_en", "is_internal_item",
                         "is_category_mapped", "nhanh_category_id", "nhanh_category_name", "first_order_date",
                         "last_order_date", "days_since_last_order", "product_status", "is_active"],
    "mart_dim_warehouse": list(dim_warehouse.columns),
    "mart_sales_daily": ["date_key", "shop_key", "product_key", "warehouse_key", "qty_demand", "demand_amount",
                         "qty_cancelled", "qty_returned", "revenue_by_created_amount", "demand_line_count",
                         "qty_revenue", "revenue_gross_amount", "revenue_discount_amount", "revenue_amount",
                         "platform_fee_amount", "net_received_amount", "revenue_line_count", "_loaded_at"],
    "mart_sku_demand_daily": ["date_key", "shop_key", "product_key", "warehouse_key", "qty_demand_unit",
                              "qty_demand_unit_from_combo", "qty_revenue_unit", "_loaded_at"],
    "mart_inventory_daily": ["date_key", "snapshot_date", "product_key", "warehouse_key", "depot_id",
                             "is_sellable_depot", "is_combo_derived", "remain_qty", "holding_qty", "shipping_qty",
                             "transferring_qty", "damaged_qty", "available_qty", "is_negative_stock",
                             "qty_demand_unit_30d", "days_of_cover", "_loaded_at"],
    "mart_orders": ["order_id", "marketplace_order_id", "created_date_key", "delivered_date_key", "shop_key",
                    "warehouse_key", "order_status_key", "created_at", "created_date", "confirmed_at", "packed_at",
                    "sent_to_carrier_at", "delivered_at", "delivered_date", "created_hour", "status_code",
                    "status_name", "status_group", "is_demand", "is_revenue", "is_cancelled", "is_returned",
                    "sale_channel_code", "sale_channel_name", "is_marketplace", "shop_id", "depot_id",
                    "order_type_code", "reason_code", "original_order_id", "carrier_id", "carrier_name",
                    "carrier_service_type_code", "city_id", "district_id", "line_count", "sku_count", "qty_total",
                    "qty_unit_total", "has_combo", "has_free_item", "has_test_product", "is_test_order",
                    "gross_amount", "line_discount_amount", "lines_total_amount", "order_discount_amount",
                    "platform_fee_amount", "is_platform_fee_missing", "net_received_amount", "ship_fee_amount",
                    "customer_ship_fee_amount", "cod_amount", "transfer_amount", "hours_to_confirm",
                    "hours_to_ship", "hours_to_deliver", "is_negative_payment", "is_time_anomaly", "updated_at",
                    "_loaded_at"],
    "mart_order_lines": ["order_line_id", "order_id", "line_no", "product_key", "shop_key", "warehouse_key",
                         "order_status_key", "created_date_key", "delivered_date_key", "created_date",
                         "delivered_date", "status_code", "status_group", "is_demand", "is_revenue",
                         "sale_channel_code", "product_id", "is_combo", "is_free_item", "qty", "unit_price",
                         "line_subtotal", "line_discount_amount", "line_total_amount", "platform_fee_alloc_amount",
                         "net_received_amount", "_loaded_at"],
}
FRAMES = {
    "mart_dim_date": dim_date, "mart_dim_shop": shops, "mart_dim_product": products,
    "mart_dim_warehouse": dim_warehouse, "mart_sales_daily": sales_daily, "mart_sku_demand_daily": sku_daily,
    "mart_inventory_daily": inv, "mart_orders": o, "mart_order_lines": lines,
}
for c in ("created_date", "delivered_date"):
    o[c] = o[c].dt.date
    lines[c] = lines[c].dt.date

OUT_DIR.mkdir(parents=True, exist_ok=True)
for name, df in FRAMES.items():
    out = df[COLS[name]]
    out.to_csv(OUT_DIR / f"{name}.csv", index=False, date_format="%Y-%m-%d %H:%M:%S")
    print(f"{name:24s} {len(out):>9,} rows")
