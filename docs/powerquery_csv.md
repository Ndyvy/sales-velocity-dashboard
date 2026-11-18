# Power Query (M) cho 9 bảng

Mỗi khối dưới đây dán vào **Advanced Editor** của bảng có cùng tên, thay toàn bộ code cũ.

## mart_dim_date

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_dim_date.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"date_key", Int64.Type},
        {"date_day", type date},
        {"year_num", Int64.Type},
        {"quarter_num", Int64.Type},
        {"month_num", Int64.Type},
        {"year_month", type text},
        {"iso_week_num", Int64.Type},
        {"iso_week_year", Int64.Type},
        {"day_of_week_num", Int64.Type},
        {"day_of_month_num", Int64.Type},
        {"is_weekend", type logical},
        {"month_start_date", type date},
        {"same_day_last_year_date", type date}
    }, "en-US")
in
    Typed
```

## mart_dim_shop

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_dim_shop.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"shop_key", Int64.Type},
        {"sale_channel_code", Int64.Type},
        {"sale_channel_name", type text},
        {"is_marketplace", type logical},
        {"shop_id", type text},
        {"shop_label", type text},
        {"shop_name", type text},
        {"platform_shop_name", type text},
        {"brand", type text},
        {"region", type text},
        {"is_shop_active", type logical},
        {"is_shop_named", type logical},
        {"first_order_date", type date},
        {"last_order_date", type date},
        {"days_since_last_order", Int64.Type}
    }, "en-US")
in
    Typed
```

## mart_dim_product

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_dim_product.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"product_key", Int64.Type},
        {"product_id", Int64.Type},
        {"sku_code", type text},
        {"product_name", type text},
        {"product_type_code", Int64.Type},
        {"is_combo", type logical},
        {"is_test_product", type logical},
        {"category_name", type text},
        {"brand_id", Int64.Type},
        {"brand_name", type text},
        {"retail_price", Int64.Type},
        {"created_date", type date},
        {"attributes_as_of_date", type date},
        {"category_name_en", type text},
        {"is_internal_item", type logical},
        {"is_category_mapped", type logical},
        {"nhanh_category_id", Int64.Type},
        {"nhanh_category_name", type text},
        {"first_order_date", type date},
        {"last_order_date", type date},
        {"days_since_last_order", Int64.Type},
        {"product_status", type text},
        {"is_active", type logical}
    }, "en-US")
in
    Typed
```

## mart_dim_warehouse

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_dim_warehouse.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"warehouse_key", Int64.Type},
        {"depot_id", Int64.Type},
        {"depot_code", type text},
        {"depot_name", type text},
        {"city_name", type text},
        {"is_sellable_depot", type logical}
    }, "en-US")
in
    Typed
```

## mart_sales_daily

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_sales_daily.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"date_key", Int64.Type},
        {"shop_key", Int64.Type},
        {"product_key", Int64.Type},
        {"warehouse_key", Int64.Type},
        {"qty_demand", Int64.Type},
        {"demand_amount", Int64.Type},
        {"qty_cancelled", Int64.Type},
        {"qty_returned", Int64.Type},
        {"revenue_by_created_amount", Int64.Type},
        {"demand_line_count", Int64.Type},
        {"qty_revenue", Int64.Type},
        {"revenue_gross_amount", type number},
        {"revenue_discount_amount", type number},
        {"revenue_amount", Int64.Type},
        {"platform_fee_amount", Int64.Type},
        {"net_received_amount", Int64.Type},
        {"revenue_line_count", Int64.Type},
        {"_loaded_at", type datetime}
    }, "en-US")
in
    Typed
```

## mart_sku_demand_daily

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_sku_demand_daily.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"date_key", Int64.Type},
        {"shop_key", Int64.Type},
        {"product_key", Int64.Type},
        {"warehouse_key", Int64.Type},
        {"qty_demand_unit", Int64.Type},
        {"qty_demand_unit_from_combo", Int64.Type},
        {"qty_revenue_unit", Int64.Type},
        {"_loaded_at", type datetime}
    }, "en-US")
in
    Typed
```

## mart_inventory_daily

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_inventory_daily.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"date_key", Int64.Type},
        {"snapshot_date", type date},
        {"product_key", Int64.Type},
        {"warehouse_key", Int64.Type},
        {"depot_id", Int64.Type},
        {"is_sellable_depot", type logical},
        {"is_combo_derived", type logical},
        {"remain_qty", Int64.Type},
        {"holding_qty", Int64.Type},
        {"shipping_qty", Int64.Type},
        {"transferring_qty", Int64.Type},
        {"damaged_qty", Int64.Type},
        {"available_qty", Int64.Type},
        {"is_negative_stock", type logical},
        {"qty_demand_unit_30d", Int64.Type},
        {"days_of_cover", type number},
        {"_loaded_at", type datetime}
    }, "en-US")
in
    Typed
```

## mart_orders

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_orders.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"order_id", Int64.Type},
        {"marketplace_order_id", type text},
        {"created_date_key", Int64.Type},
        {"delivered_date_key", Int64.Type},
        {"shop_key", Int64.Type},
        {"warehouse_key", Int64.Type},
        {"order_status_key", Int64.Type},
        {"created_at", type datetime},
        {"created_date", type date},
        {"confirmed_at", type datetime},
        {"packed_at", type datetime},
        {"sent_to_carrier_at", type datetime},
        {"delivered_at", type datetime},
        {"delivered_date", type date},
        {"created_hour", Int64.Type},
        {"status_code", Int64.Type},
        {"status_name", type text},
        {"status_group", type text},
        {"is_demand", type logical},
        {"is_revenue", type logical},
        {"is_cancelled", type logical},
        {"is_returned", type logical},
        {"sale_channel_code", Int64.Type},
        {"sale_channel_name", type text},
        {"is_marketplace", type logical},
        {"shop_id", type text},
        {"depot_id", Int64.Type},
        {"order_type_code", Int64.Type},
        {"reason_code", Int64.Type},
        {"original_order_id", Int64.Type},
        {"carrier_id", Int64.Type},
        {"carrier_name", type text},
        {"carrier_service_type_code", Int64.Type},
        {"city_id", Int64.Type},
        {"district_id", Int64.Type},
        {"line_count", Int64.Type},
        {"sku_count", Int64.Type},
        {"qty_total", Int64.Type},
        {"qty_unit_total", Int64.Type},
        {"has_combo", type logical},
        {"has_free_item", type logical},
        {"has_test_product", type logical},
        {"is_test_order", type logical},
        {"gross_amount", type number},
        {"line_discount_amount", type number},
        {"lines_total_amount", Int64.Type},
        {"order_discount_amount", Int64.Type},
        {"platform_fee_amount", Int64.Type},
        {"is_platform_fee_missing", type logical},
        {"net_received_amount", Int64.Type},
        {"ship_fee_amount", Int64.Type},
        {"customer_ship_fee_amount", Int64.Type},
        {"cod_amount", Int64.Type},
        {"transfer_amount", Int64.Type},
        {"hours_to_confirm", type number},
        {"hours_to_ship", type number},
        {"hours_to_deliver", type number},
        {"is_negative_payment", type logical},
        {"is_time_anomaly", type logical},
        {"updated_at", type datetime},
        {"_loaded_at", type datetime}
    }, "en-US")
in
    Typed
```

## mart_order_lines

```
let
    Source = Csv.Document(
        File.Contents(DataFolder & "mart_order_lines.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"order_line_id", Int64.Type},
        {"order_id", Int64.Type},
        {"line_no", Int64.Type},
        {"product_key", Int64.Type},
        {"shop_key", Int64.Type},
        {"warehouse_key", Int64.Type},
        {"order_status_key", Int64.Type},
        {"created_date_key", Int64.Type},
        {"delivered_date_key", Int64.Type},
        {"created_date", type date},
        {"delivered_date", type date},
        {"status_code", Int64.Type},
        {"status_group", type text},
        {"is_demand", type logical},
        {"is_revenue", type logical},
        {"sale_channel_code", Int64.Type},
        {"product_id", Int64.Type},
        {"is_combo", type logical},
        {"is_free_item", type logical},
        {"qty", Int64.Type},
        {"unit_price", type number},
        {"line_subtotal", type number},
        {"line_discount_amount", type number},
        {"line_total_amount", Int64.Type},
        {"platform_fee_alloc_amount", Int64.Type},
        {"net_received_amount", Int64.Type},
        {"_loaded_at", type datetime}
    }, "en-US")
in
    Typed
```
