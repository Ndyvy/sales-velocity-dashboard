# DAX measures

All measures from the report, exported with `INFO.VIEW.MEASURES()`. Most live in the `MeasuresOrders` table and are grouped by display folder.

## (no folder)

### Orders Placed
*Table: `mart_sales_daily`*

```DAX
Orders Placed =
SUM('mart_sales_daily'[qty_demand])
```

### Phụ đề kỳ
*Table: `mart_sales_daily`*

```DAX
Phụ đề kỳ =
VAR _s = MIN ( mart_dim_date[date_day] )
VAR _e = MAX ( mart_dim_date[date_day] )
RETURN
    FORMAT ( _s, "dd/MM/yyyy" ) & " – " & FORMAT ( _e, "dd/MM/yyyy" ) & " · "
        & ( DATEDIFF ( _s, _e, DAY ) + 1 ) & " ngày · Lighter bars = Previous period"
```

### Qty Demand Kỳ trước
*Table: `mart_sales_daily`*

```DAX
Qty Demand Kỳ trước =
VAR _start = MIN ( mart_dim_date[date_day] )
VAR _end   = MAX ( mart_dim_date[date_day] )
VAR _len   = DATEDIFF ( _start, _end, DAY ) + 1
RETURN
    CALCULATE (
        SUM ( mart_sales_daily[qty_demand] ),
        CROSSFILTER ( Group_by[date_key], mart_dim_date[date_key], NONE ),
        REMOVEFILTERS ( mart_dim_date ),
        REMOVEFILTERS ( Group_by ),
        mart_dim_date[date_day] >= _start - _len,
        mart_dim_date[date_day] <= _start - 1
    )
```

### Demand Orders
*Table: `MeasuresOrders`*

```DAX
Demand Orders =
CALCULATE (
    DISTINCTCOUNT ( mart_orders[order_id] ),
    mart_orders[is_demand] = TRUE ()
)
```

### Successful Orders
*Table: `MeasuresOrders`*

```DAX
Successful Orders =
CALCULATE (
    DISTINCTCOUNT ( mart_orders[order_id] ),
    mart_orders[is_demand] = TRUE (),
    mart_orders[is_revenue] = TRUE ()
)
```

### Success Rate
*Table: `MeasuresOrders`*

```DAX
Success Rate =
DIVIDE ( [Successful Orders], [Demand Orders] )
```

### Đơn nhu cầu KT
*Table: `MeasuresOrders`*

```DAX
Đơn nhu cầu KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [Demand Orders],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### Đơn thành công KT
*Table: `MeasuresOrders`*

```DAX
Đơn thành công KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [Successful Orders],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### Tỉ lệ thành công KT
*Table: `MeasuresOrders`*

```DAX
Tỉ lệ thành công KT =
DIVIDE ( [Đơn thành công KT], [Đơn nhu cầu KT] )
```

### Đơn TC %Δ
*Table: `MeasuresOrders`*

```DAX
Đơn TC %Δ =
DIVIDE ( [Successful Orders] - [Đơn thành công KT], [Đơn thành công KT] )
```

### Tỉ lệ Δ điểm
*Table: `MeasuresOrders`*

```DAX
Tỉ lệ Δ điểm =
( [Success Rate] - [Tỉ lệ thành công KT] ) * 100
```

### Unusually high
*Table: `MeasuresOrders`*

```DAX
Unusually high =
VAR NguongCao = 0.4
VAR v = [Current period]
VAR b = [_Baseline chọn]
RETURN
IF (
    ISINSCOPE ( mart_dim_date[date_day] ) && NOT ISBLANK ( b ),
    IF ( v > b * ( 1 + NguongCao ), v )
)
```

### Unusually low
*Table: `MeasuresOrders`*

```DAX
Unusually low =
VAR NguongThap = 0.2
VAR v = [Current period]
VAR b = [_Baseline chọn]
RETURN
IF (
    ISINSCOPE ( mart_dim_date[date_day] ) && NOT ISBLANK ( b ),
    IF ( v < b * ( 1 - NguongThap ), v )
)
```

### Tiêu đề chart chọn
*Table: `MeasuresOrders`*

```DAX
Tiêu đề chart chọn =
SWITCH (
    [Chỉ số đang chọn],
    "Demand Orders",      "Demand Orders by Day",
    "Successful Orders",  "Successful Orders by Day",
    "Success Rate",       "Success Rate by Day",
    "Order Quantity",     "Order Quantity by Day",
    "Successful Revenue", "Successful Revenue by Day",
    "Orders / Day",       "Orders per Day",
    [Chỉ số đang chọn] & " by Day"
)
```

### Đơn NC %Δ
*Table: `MeasuresOrders`*

```DAX
Đơn NC %Δ =
DIVIDE ( [Demand Orders] - [Đơn nhu cầu KT], [Đơn nhu cầu KT] )
```

### Order Quantity
*Table: `MeasuresOrders`*

```DAX
Order Quantity =
CALCULATE (
    SUM ( mart_orders[qty_unit_total] ),
    mart_orders[is_demand] = TRUE ()
)
```

### Số lượng đặt KT
*Table: `MeasuresOrders`*

```DAX
Số lượng đặt KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [Order Quantity],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### SL đặt Δ label
*Table: `MeasuresOrders`*

```DAX
SL đặt Δ label =
VAR d = [SL đặt %Δ]
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0.0%" ) & " vs previous period" )
```

### Doanh thu thành công
*Table: `MeasuresOrders`*

```DAX
Doanh thu thành công =
CALCULATE (
    SUM ( mart_orders[cod_amount] ),
    mart_orders[is_demand] = TRUE (),
    mart_orders[is_revenue] = TRUE ()
)
```

### Doanh thu thành công KT
*Table: `MeasuresOrders`*

```DAX
Doanh thu thành công KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [Doanh thu thành công],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### DT Δ label
*Table: `MeasuresOrders`*

```DAX
DT Δ label =
VAR d = [DT %Δ]
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0.0%" ) & " vs previous period" )
```

### Successful Revenue
*Table: `MeasuresOrders`*

```DAX
Successful Revenue =
VAR v = [Doanh thu thành công]
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( v ),     "–",
    v >= 1000000000,   FORMAT ( v / 1000000000, "#,0.00" ) & " billion",
    v >= 1000000,      FORMAT ( v / 1000000, "#,0.0" ) & " million",
    FORMAT ( v, "#,0" )
)
```

### Đơn nhu cầu
*Table: `MeasuresOrders`*

```DAX
Đơn nhu cầu =
CALCULATE ( DISTINCTCOUNT ( mart_orders[order_id] ), mart_orders[is_demand] = TRUE () )
```

### Orders / Day
*Table: `MeasuresOrders`*

```DAX
Orders / Day =
AVERAGEX (
    VALUES ( mart_dim_date[date_day] ),
    [Đơn nhu cầu]
)
```

### Đơn mỗi ngày KT
*Table: `MeasuresOrders`*

```DAX
Đơn mỗi ngày KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [Đơn nhu cầu],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### Đơn/ngày Δ label
*Table: `MeasuresOrders`*

```DAX
Đơn/ngày Δ label =
VAR d = [Đơn/ngày %Δ]
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0.0%" ) & " vs previous period" )
```

### Chỉ số đang chọn
*Table: `MeasuresOrders`*

```DAX
Chỉ số đang chọn =
SELECTEDVALUE ( 'Chỉ số'[Chỉ số], "Demand Orders" )
```

### Current period
*Table: `MeasuresOrders`*

```DAX
Current period =
SWITCH (
    [Chỉ số đang chọn],
    "Demand Orders",      [Đơn nhu cầu],
    "Successful Orders",  [Successful Orders],
    "Success Rate",       [Success Rate],
    "Order Quantity",     [Order Quantity],
    "Successful Revenue", [Doanh thu thành công],
    "Orders / Day",       [Đơn nhu cầu]
)
```

### Previous period
*Table: `MeasuresOrders`*

```DAX
Previous period =
SWITCH (
    [Chỉ số đang chọn],
    "Demand Orders",      [Đơn nhu cầu KT],
    "Successful Orders",  [Đơn thành công KT],
    "Success Rate",       [Tỉ lệ thành công KT],
    "Order Quantity",     [Số lượng đặt KT],
    "Successful Revenue", [Doanh thu thành công KT],
    "Orders / Day",       [Đơn nhu cầu KT]
)
```

### _Baseline chọn
*Table: `MeasuresOrders`*

```DAX
_Baseline chọn =
VAR d      = MAX ( mart_dim_date[date_day] )
VAR batDau = MAX ( d - 28, DATE ( YEAR ( d ), 1, 1 ) )
VAR ketThuc = d - 1
VAR soNgay =
    CALCULATE (
        COUNTROWS ( VALUES ( mart_dim_date[date_day] ) ),
        REMOVEFILTERS ( mart_dim_date ),
        REMOVEFILTERS ( Group_by ),
        mart_dim_date[date_day] >= batDau,
        mart_dim_date[date_day] <= ketThuc
    )
RETURN
IF (
    soNgay >= 7,
    CALCULATE (
        MEDIANX ( VALUES ( mart_dim_date[date_day] ), [Current period] ),
        REMOVEFILTERS ( mart_dim_date ),
        REMOVEFILTERS ( Group_by ),
        mart_dim_date[date_day] >= batDau,
        mart_dim_date[date_day] <= ketThuc
    )
)
```

### Tỉ trọng
*Table: `MeasuresOrders`*

```DAX
Tỉ trọng =
VAR v = [Đơn nhu cầu]
RETURN
SWITCH (
    TRUE (),
    ISINSCOPE ( mart_dim_shop[shop_name] ),
        DIVIDE (
            v,
            CALCULATE (
                [Đơn nhu cầu],
                ALLSELECTED ( mart_dim_shop[shop_name], mart_dim_shop[Shop_Thứ tự SL] )
            )
        ),
    ISINSCOPE ( mart_dim_shop[Channel_name] ),
        DIVIDE ( v, CALCULATE ( [Đơn nhu cầu], ALLSELECTED ( mart_dim_shop ) ) ),
    1
)
```

### Thay đổi
*Table: `MeasuresOrders`*

```DAX
Thay đổi =
VAR d = [Đơn NC %Δ]
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) )
```

### Thay đổi nền
*Table: `MeasuresOrders`*

```DAX
Thay đổi nền =
IF ( [Đơn NC %Δ] >= 0, "#E3F4EA", "#FBE3E3" )
```

### SL bán
*Table: `MeasuresOrders`*

```DAX
SL bán =
CALCULATE (
    SUM ( mart_order_lines[qty] ),
    mart_order_lines[is_demand] = TRUE (),
    mart_order_lines[is_free_item] = FALSE ()
)
```

### SL bán KT
*Table: `MeasuresOrders`*

```DAX
SL bán KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [SL bán],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### % trong shop
*Table: `MeasuresOrders`*

```DAX
% trong shop =
DIVIDE ( [SL bán], CALCULATE ( [SL bán], ALLSELECTED ( mart_dim_product ) ) )
```

### Doanh thu category
*Table: `MeasuresOrders`*

```DAX
Doanh thu category =
CALCULATE (
    SUM ( mart_order_lines[line_total_amount] ),
    mart_order_lines[is_demand] = TRUE (),
    mart_order_lines[is_revenue] = TRUE ()
)
```

### SL bán %Δ
*Table: `MeasuresOrders`*

```DAX
SL bán %Δ =
DIVIDE ( [SL bán] - [SL bán KT], [SL bán KT] )
```

### SL bán so với KT
*Table: `MeasuresOrders`*

```DAX
SL bán so với KT =
VAR d = DIVIDE ( [SL bán] - [SL bán KT], [SL bán KT] )
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) )
```

### Tiêu đề category
*Table: `MeasuresOrders`*

```DAX
Tiêu đề category =
"Top category – "
    & SWITCH (
        TRUE (),
        HASONEVALUE ( mart_dim_shop[shop_name] ),    VALUES ( mart_dim_shop[shop_name] ),
        HASONEVALUE ( mart_dim_shop[Channel_name] ), VALUES ( mart_dim_shop[Channel_name] ),
        "All shops"
    )
```

### _Sắp category
*Table: `MeasuresOrders`*

```DAX
_Sắp category =
CALCULATE (
    [SL bán],
    ALLSELECTED ( mart_dim_shop[shop_name], mart_dim_shop[Shop_Thứ tự SL] )
)
```

### SL shop dẫn đầu
*Table: `MeasuresOrders`*

```DAX
SL shop dẫn đầu =
VAR shops =
    FILTER (
        CALCULATETABLE (
            ADDCOLUMNS (
                VALUES ( mart_dim_shop[shop_name] ),
                "@v", CALCULATE ( [SL bán], ALLSELECTED ( mart_dim_product ) )
            ),
            ALLSELECTED ( mart_dim_shop[shop_name], mart_dim_shop[Shop_Thứ tự SL] )
        ),
        NOT ISBLANK ( [@v] )
    )
VAR s = MAXX ( TOPN ( 1, shops, [@v], DESC ), mart_dim_shop[shop_name] )
RETURN
CALCULATE (
    [SL bán],
    REMOVEFILTERS ( mart_dim_shop[shop_name], mart_dim_shop[Shop_Thứ tự SL] ),
    mart_dim_shop[shop_name] = s
)
```

### Phụ đề chart chọn
*Table: `MeasuresOrders`*

```DAX
Phụ đề chart chọn =
VAR s = MIN ( mart_dim_date[date_day] )
VAR e = MAX ( mart_dim_date[date_day] )
VAR n = INT ( e - s ) + 1
RETURN
FORMAT ( s, "dd/MM/yyyy" ) & " – " & FORMAT ( e, "dd/MM/yyyy" )
    & " · " & n & " days"
    & " · dashed = previous period (" & FORMAT ( s - n, "dd/MM" ) & " – " & FORMAT ( s - 1, "dd/MM" ) & ")"
    & " · red / blue dots = unusually high / low vs last 28 days"
```

### Giá trị chọn – kênh
*Table: `MeasuresOrders`*

```DAX
Giá trị chọn – kênh =
SWITCH (
    [Chỉ số đang chọn],
    "Successful Orders",  [Successful Orders],
    "Order Quantity",     [Order Quantity],
    "Successful Revenue", [Doanh thu thành công],
    [Đơn nhu cầu]
)
```

### Chỉ số hiển thị – kênh
*Table: `MeasuresOrders`*

```DAX
Chỉ số hiển thị – kênh =
IF (
    [Chỉ số đang chọn] IN { "Success Rate", "Orders / Day" },
    "Demand Orders",
    [Chỉ số đang chọn]
)
```

### Tiêu đề chart kênh
*Table: `MeasuresOrders`*

```DAX
Tiêu đề chart kênh =
[Chỉ số hiển thị – kênh] & " by Channel"
```

### Phụ đề chart kênh
*Table: `MeasuresOrders`*

```DAX
Phụ đề chart kênh =
IF (
    [Chỉ số đang chọn] IN { "Success Rate", "Orders / Day" },
    "Stacked by channel · " & [Chỉ số đang chọn] & " can't be stacked, showing Demand Orders",
    "Stacked by channel · hover to see each channel's share"
)
```

### Tỷ trọng kênh (chọn)
*Table: `MeasuresOrders`*

```DAX
Tỷ trọng kênh (chọn) =
DIVIDE (
    [Giá trị chọn – kênh],
    CALCULATE ( [Giá trị chọn – kênh], ALLSELECTED ( mart_dim_shop ) )
)
```

### Giá trị chọn – bảng
*Table: `MeasuresOrders`*

```DAX
Giá trị chọn – bảng =
SWITCH (
    [Chỉ số đang chọn],
    "Successful Orders",  [Successful Orders],
    "Success Rate",       [Success Rate],
    "Order Quantity",     [Order Quantity],
    "Successful Revenue", [Doanh thu thành công],
    "Orders / Day",       [Orders / Day],
    [Đơn nhu cầu]
)
```

### Giá trị chọn – bảng KT
*Table: `MeasuresOrders`*

```DAX
Giá trị chọn – bảng KT =
SWITCH (
    [Chỉ số đang chọn],
    "Successful Orders",  [Đơn thành công KT],
    "Success Rate",       [Tỉ lệ thành công KT],
    "Order Quantity",     [Số lượng đặt KT],
    "Successful Revenue", [Doanh thu thành công KT],
    "Orders / Day",       [Đơn mỗi ngày KT],
    [Đơn nhu cầu KT]
)
```

### Tỉ trọng (chọn)
*Table: `MeasuresOrders`*

```DAX
Tỉ trọng (chọn) =
VAR v = [Giá trị chọn – bảng]
RETURN
IF (
    [Chỉ số đang chọn] <> "Success Rate",
    SWITCH (
        TRUE (),
        ISINSCOPE ( mart_dim_shop[shop_name] ),
            DIVIDE ( v, CALCULATE ( [Giá trị chọn – bảng],
                ALLSELECTED ( mart_dim_shop[shop_name], mart_dim_shop[Shop_Thứ tự SL] ) ) ),
        ISINSCOPE ( mart_dim_shop[Channel_name] ),
            DIVIDE ( v, CALCULATE ( [Giá trị chọn – bảng], ALLSELECTED ( mart_dim_shop ) ) ),
        1
    )
)
```

### _Δ chọn
*Table: `MeasuresOrders`*

```DAX
_Δ chọn =
IF (
    [Chỉ số đang chọn] = "Success Rate",
    ( [Giá trị chọn – bảng] - [Giá trị chọn – bảng KT] ) * 100,
    DIVIDE ( [Giá trị chọn – bảng] - [Giá trị chọn – bảng KT], [Giá trị chọn – bảng KT] )
)
```

### Thay đổi (chọn)
*Table: `MeasuresOrders`*

```DAX
Thay đổi (chọn) =
VAR d = [_Δ chọn]
RETURN
IF (
    NOT ISBLANK ( [Giá trị chọn – bảng] ),
    IF (
        ISBLANK ( d ), "–",
        IF ( d >= 0, "▲ ", "▼ " )
            & IF ( [Chỉ số đang chọn] = "Success Rate",
                   FORMAT ( ABS ( d ), "0.0" ) & " pts",
                   FORMAT ( ABS ( d ), "0%" ) )
    )
)
```

### Thay đổi màu (chọn)
*Table: `MeasuresOrders`*

```DAX
Thay đổi màu (chọn) =
IF ( [_Δ chọn] >= 0, "#1E8E5A", "#C62828" )
```

### Thay đổi nền (chọn)
*Table: `MeasuresOrders`*

```DAX
Thay đổi nền (chọn) =
IF ( [_Δ chọn] >= 0, "#E3F4EA", "#FBE3E3" )
```

### Tổng ngày (chọn)
*Table: `MeasuresOrders`*

```DAX
Tổng ngày (chọn) =
CALCULATE ( [Giá trị chọn – kênh], ALLSELECTED ( mart_dim_shop ) )
```

## 1.Card

### Đơn TC Δ label
*Table: `MeasuresOrders`*

```DAX
Đơn TC Δ label =
VAR d = [Đơn TC %Δ]
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) & " vs previous period" )
```

### Đơn TC Δ màu
*Table: `MeasuresOrders`*

```DAX
Đơn TC Δ màu =
IF ( [Đơn TC %Δ] >= 0, "#1E8E5A", "#C62828" )
```

### Tỉ lệ Δ label
*Table: `MeasuresOrders`*

```DAX
Tỉ lệ Δ label =
VAR d = [Tỉ lệ Δ điểm]
RETURN
IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0.0" ) & " pts vs previous period"
```

### Tỉ lệ Δ màu
*Table: `MeasuresOrders`*

```DAX
Tỉ lệ Δ màu =
IF ( [Tỉ lệ Δ điểm] >= 0, "#1E8E5A", "#C62828" )
```

### Đơn NC Δ label
*Table: `MeasuresOrders`*

```DAX
Đơn NC Δ label =
VAR d = [Đơn NC %Δ]
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) & " vs previous period" )
```

### Đơn NC Δ màu
*Table: `MeasuresOrders`*

```DAX
Đơn NC Δ màu =
IF ( [Đơn NC %Δ] >= 0, "#1E8E5A", "#C62828" )
```

### SL đặt %Δ
*Table: `MeasuresOrders`*

```DAX
SL đặt %Δ =
DIVIDE ( [Order Quantity] - [Số lượng đặt KT], [Số lượng đặt KT] )
```

### DT %Δ
*Table: `MeasuresOrders`*

```DAX
DT %Δ =
DIVIDE ( [Doanh thu thành công] - [Doanh thu thành công KT], [Doanh thu thành công KT] )
```

### Đơn/ngày %Δ
*Table: `MeasuresOrders`*

```DAX
Đơn/ngày %Δ =
DIVIDE ( [Đơn nhu cầu] - [Đơn mỗi ngày KT], [Đơn mỗi ngày KT] )
```

### SL đặt Δ màu
*Table: `MeasuresOrders`*

```DAX
SL đặt Δ màu =
IF ( [SL đặt %Δ] >= 0, "#1E8E5A", "#C62828" )
```

### DT Δ màu
*Table: `MeasuresOrders`*

```DAX
DT Δ màu =
IF ( [DT %Δ] >= 0, "#1E8E5A", "#C62828" )
```

### Đơn/ngày Δ màu
*Table: `MeasuresOrders`*

```DAX
Đơn/ngày Δ màu =
IF ( [Đơn/ngày %Δ] >= 0, "#1E8E5A", "#C62828" )
```

## 7. Huỷ & hoàn

### Tổng đơn tạo
*Table: `MeasuresOrders`*

```DAX
Tổng đơn tạo =
CALCULATE ( COUNTROWS ( mart_orders ), mart_orders[is_test_order] = FALSE () )
```

### Đơn huỷ
*Table: `MeasuresOrders`*

```DAX
Đơn huỷ =
CALCULATE (
    COUNTROWS ( mart_orders ),
    mart_orders[is_cancelled] = TRUE (),
    mart_orders[is_test_order] = FALSE ()
)
```

### Đơn hoàn
*Table: `MeasuresOrders`*

```DAX
Đơn hoàn =
CALCULATE (
    COUNTROWS ( mart_orders ),
    mart_orders[is_returned] = TRUE (),
    mart_orders[is_test_order] = FALSE ()
)
```

### Cancel rate
*Table: `MeasuresOrders`*

```DAX
Cancel rate =
VAR d = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    DIVIDE ( [Đơn huỷ], [Tổng đơn tạo] ),
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] > d - 7,
    mart_dim_date[date_day] <= d
)
```

### Tỷ lệ hoàn 7N
*Table: `MeasuresOrders`*

```DAX
Tỷ lệ hoàn 7N =
VAR d = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    DIVIDE ( [Đơn hoàn], [Tổng đơn tạo] ),
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] > d - 7,
    mart_dim_date[date_day] <= d
)
```

### _Ngày dữ liệu mới nhất
*Table: `MeasuresOrders`*

```DAX
_Ngày dữ liệu mới nhất =
VAR k =
    CALCULATE ( MAX ( mart_orders[created_date_key] ), REMOVEFILTERS () )
RETURN
LOOKUPVALUE ( mart_dim_date[date_day], mart_dim_date[date_key], k )
```

### Return rate
*Table: `MeasuresOrders`*

```DAX
Return rate =
IF ( MAX ( mart_dim_date[date_day] ) <= [_Ngày dữ liệu mới nhất] - 14, [Tỷ lệ hoàn 7N] )
```

### Return rate (incomplete)
*Table: `MeasuresOrders`*

```DAX
Return rate (incomplete) =
IF ( MAX ( mart_dim_date[date_day] ) >= [_Ngày dữ liệu mới nhất] - 14, [Tỷ lệ hoàn 7N] )
```

## 0.Viền

### Viền Demand
*Table: `MeasuresOrders`*

```DAX
Viền Demand =
IF ( [Chỉ số đang chọn] = "Demand Orders", "#B5335C", "#E6E6E6" )
```

### Viền Successful
*Table: `MeasuresOrders`*

```DAX
Viền Successful =
IF ( [Chỉ số đang chọn] = "Successful Orders", "#B5335C", "#E6E6E6" )
```

### Viền Rate
*Table: `MeasuresOrders`*

```DAX
Viền Rate =
IF ( [Chỉ số đang chọn] = "Success Rate", "#B5335C", "#E6E6E6" )
```

### Viền Revenue
*Table: `MeasuresOrders`*

```DAX
Viền Revenue =
IF ( [Chỉ số đang chọn] = "Successful Revenue", "#B5335C", "#E6E6E6" )
```

### Viền Per Day
*Table: `MeasuresOrders`*

```DAX
Viền Per Day =
IF ( [Chỉ số đang chọn] = "Orders / Day", "#B5335C", "#E6E6E6" )
```

### Viền Quantity
*Table: `MeasuresOrders`*

```DAX
Viền Quantity =
IF ( [Chỉ số đang chọn] = "Order Quantity", "#B5335C", "#E6E6E6" )
```

## Page2.Category

### Đơn có SP
*Table: `MeasuresOrders`*

```DAX
Đơn có SP =
CALCULATE (
    DISTINCTCOUNT ( mart_order_lines[order_id] ),
    mart_order_lines[is_demand] = TRUE ()
)
```

### SL thành công
*Table: `MeasuresOrders`*

```DAX
SL thành công =
CALCULATE (
    SUM ( mart_order_lines[qty] ),
    mart_order_lines[is_demand] = TRUE (),
    mart_order_lines[is_revenue] = TRUE (),
    mart_order_lines[is_free_item] = FALSE ()
)
```

### DT thành công (tr)
*Table: `MeasuresOrders`*

```DAX
DT thành công (tr) =
DIVIDE ( [Doanh thu category], 1000000 )
```

### SL Δ label
*Table: `MeasuresOrders`*

```DAX
SL Δ label =
VAR d = [SL bán %Δ]
RETURN
IF (
    NOT ISBLANK ( [SL bán] ),
    IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0.0%" ) )
)
```

### SL Δ màu
*Table: `MeasuresOrders`*

```DAX
SL Δ màu =
IF ( [SL bán %Δ] >= 0, "#1E8E5A", "#C62828" )
```

### SL Δ nền
*Table: `MeasuresOrders`*

```DAX
SL Δ nền =
IF ( [SL bán %Δ] >= 0, "#E3F4EA", "#FBE3E3" )
```

## page2.chartline

### Tiêu đề trend SP
*Table: `MeasuresOrders`*

```DAX
Tiêu đề trend SP =
"Daily units – "
    & SWITCH (
        TRUE (),
        HASONEVALUE ( mart_dim_product[Product] ),         VALUES ( mart_dim_product[Product] ),
        HASONEVALUE ( mart_dim_product[category_name_en] ), VALUES ( mart_dim_product[category_name_en] ),
        "All products"
    )
```

### Ngày kỳ trước
*Table: `MeasuresOrders`*

```DAX
Ngày kỳ trước =
VAR s = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n = INT ( e - s ) + 1
RETURN FORMAT ( MAX ( mart_dim_date[date_day] ) - n, "dd/MM/yyyy" )
```

## Page3.Combo

### SL lẻ tổng
*Table: `MeasuresOrders`*

```DAX
SL lẻ tổng =
SUM ( mart_sku_demand_daily[qty_demand_unit] )
```

### SL đi theo combo
*Table: `MeasuresOrders`*

```DAX
SL đi theo combo =
SUM ( mart_sku_demand_daily[qty_demand_unit_from_combo] )
```

### SL bán riêng
*Table: `MeasuresOrders`*

```DAX
SL bán riêng =
[SL lẻ tổng] - [SL đi theo combo]
```

### Tỉ trọng qua combo
*Table: `MeasuresOrders`*

```DAX
Tỉ trọng qua combo =
DIVIDE ( [SL đi theo combo], [SL lẻ tổng] )
```

### Lượt combo
*Table: `MeasuresOrders`*

```DAX
Lượt combo =
CALCULATE (
    SUM ( mart_order_lines[qty] ),
    mart_order_lines[is_demand] = TRUE (),
    mart_dim_product[is_combo] = TRUE ()
)
```

### SL bán riêng KT
*Table: `MeasuresOrders`*

```DAX
SL bán riêng KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [SL bán riêng],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### SL đi theo combo KT
*Table: `MeasuresOrders`*

```DAX
SL đi theo combo KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [SL đi theo combo],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### Lượt combo KT
*Table: `MeasuresOrders`*

```DAX
Lượt combo KT =
VAR s  = CALCULATE ( MIN ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR e  = CALCULATE ( MAX ( mart_dim_date[date_day] ), ALLSELECTED ( mart_dim_date ) )
VAR n  = INT ( e - s ) + 1
VAR cs = MIN ( mart_dim_date[date_day] )
VAR ce = MAX ( mart_dim_date[date_day] )
RETURN
CALCULATE (
    [Lượt combo],
    REMOVEFILTERS ( mart_dim_date ),
    REMOVEFILTERS ( Group_by ),
    mart_dim_date[date_day] >= cs - n,
    mart_dim_date[date_day] <= ce - n
)
```

### Tỉ trọng qua combo KT
*Table: `MeasuresOrders`*

```DAX
Tỉ trọng qua combo KT =
DIVIDE ( [SL đi theo combo KT], [SL bán riêng KT] + [SL đi theo combo KT] )
```

### Bán riêng Δ label
*Table: `MeasuresOrders`*

```DAX
Bán riêng Δ label =
VAR d = DIVIDE ( [SL bán riêng] - [SL bán riêng KT], [SL bán riêng KT] )
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) & " vs previous period" )
```

### Combo Δ label
*Table: `MeasuresOrders`*

```DAX
Combo Δ label =
VAR d = DIVIDE ( [SL đi theo combo] - [SL đi theo combo KT], [SL đi theo combo KT] )
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) & " vs previous period" )
```

### Tỉ trọng combo Δ label
*Table: `MeasuresOrders`*

```DAX
Tỉ trọng combo Δ label =
VAR d = ( [Tỉ trọng qua combo] - [Tỉ trọng qua combo KT] ) * 100
RETURN
IF (
    ISBLANK ( [Tỉ trọng qua combo KT] ), "–",
    IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0.0" ) & " pts vs previous period"
)
```

### Lượt combo Δ label
*Table: `MeasuresOrders`*

```DAX
Lượt combo Δ label =
VAR d = DIVIDE ( [Lượt combo] - [Lượt combo KT], [Lượt combo KT] )
RETURN
IF ( ISBLANK ( d ), "–", IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" ) & " vs previous period" )
```

### Bán riêng Δ màu
*Table: `MeasuresOrders`*

```DAX
Bán riêng Δ màu =
IF ( [SL bán riêng] >= [SL bán riêng KT], "#1E8E5A", "#C62828" )
```

### Combo Δ màu
*Table: `MeasuresOrders`*

```DAX
Combo Δ màu =
IF ( [SL đi theo combo] >= [SL đi theo combo KT], "#1E8E5A", "#C62828" )
```

### Tỉ trọng combo Δ màu
*Table: `MeasuresOrders`*

```DAX
Tỉ trọng combo Δ màu =
IF ( [Tỉ trọng qua combo] >= [Tỉ trọng qua combo KT], "#1E8E5A", "#C62828" )
```

### Lượt combo Δ màu
*Table: `MeasuresOrders`*

```DAX
Lượt combo Δ màu =
IF ( [Lượt combo] >= [Lượt combo KT], "#1E8E5A", "#C62828" )
```

### Combo Δ ngắn
*Table: `MeasuresOrders`*

```DAX
Combo Δ ngắn =
VAR cur  = [SL đi theo combo]
VAR prev = [SL đi theo combo KT]
VAR d    = DIVIDE ( cur - prev, prev )
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( cur ) || cur = 0, "–",
    ISBLANK ( prev ) || prev < 20, "new",
    IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" )
)
```

## page3.top10combo

### Doanh thu combo (tr)
*Table: `MeasuresOrders`*

```DAX
Doanh thu combo (tr) =
DIVIDE (
    CALCULATE (
        SUM ( mart_order_lines[line_total_amount] ),
        mart_order_lines[is_demand] = TRUE (),
        mart_order_lines[is_revenue] = TRUE (),
        mart_dim_product[is_combo] = TRUE ()
    ),
    1000000
)
```

### Lượt combo Δ ngắn
*Table: `MeasuresOrders`*

```DAX
Lượt combo Δ ngắn =
VAR cur  = [Lượt combo]
VAR prev = [Lượt combo KT]
VAR d    = DIVIDE ( cur - prev, prev )
RETURN
SWITCH (
    TRUE (),
    ISBLANK ( cur ) || cur = 0, "–",
    ISBLANK ( prev ) || prev < 10, "new",
    IF ( d >= 0, "▲ ", "▼ " ) & FORMAT ( ABS ( d ), "0%" )
)
```

## page3.combochart3

### Tỷ trọng đơn
*Table: `MeasuresOrders`*

```DAX
Tỷ trọng đơn =
DIVIDE (
    [Đơn nhu cầu],
    CALCULATE ( [Đơn nhu cầu], REMOVEFILTERS ( mart_orders[Order type] ) )
)
```

### Giá trị đơn TB
*Table: `MeasuresOrders`*

```DAX
Giá trị đơn TB =
DIVIDE (
    CALCULATE ( SUM ( mart_orders[lines_total_amount] ), mart_orders[is_demand] = TRUE () ),
    [Đơn nhu cầu]
)
```

### SP mỗi đơn TB
*Table: `MeasuresOrders`*

```DAX
SP mỗi đơn TB =
DIVIDE (
    CALCULATE ( SUM ( mart_orders[qty_unit_total] ), mart_orders[is_demand] = TRUE () ),
    [Đơn nhu cầu]
)
```

### Tỉ lệ huỷ
*Table: `MeasuresOrders`*

```DAX
Tỉ lệ huỷ =
DIVIDE ( [Đơn huỷ], [Tổng đơn tạo] )
```
