"""
Builds a formatted, multi-sheet Excel report from the SQLite analysis results.
Output: sales_report.xlsx
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.chart import LineChart, BarChart, PieChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows

import analysis as an

HEADER_FILL = PatternFill(start_color="305496", end_color="305496", fill_type="solid")
HEADER_FONT = Font(name="Arial", bold=True, color="FFFFFF")
BODY_FONT = Font(name="Arial", size=10)
TITLE_FONT = Font(name="Arial", bold=True, size=14)


def write_df(ws, df, start_row=1, title=None):
    row = start_row
    if title:
        ws.cell(row=row, column=1, value=title).font = TITLE_FONT
        row += 2
    for r_idx, row_data in enumerate(dataframe_to_rows(df, index=False, header=True)):
        for c_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row + r_idx, column=c_idx, value=value)
            if r_idx == 0:
                cell.font = HEADER_FONT
                cell.fill = HEADER_FILL
                cell.alignment = Alignment(horizontal="center")
            else:
                cell.font = BODY_FONT
    for col_cells in ws.columns:
        length = max(len(str(c.value)) if c.value is not None else 0 for c in col_cells)
        ws.column_dimensions[col_cells[0].column_letter].width = min(max(length + 2, 10), 30)
    return row + len(df) + 1  # next free row


def main():
    conn = an.get_conn()
    monthly = an.monthly_revenue(conn)
    top_prod = an.top_products(conn)
    regional = an.regional_performance(conn)
    recency = an.customer_recency(conn)
    rfm = an.customer_rfm_segments(conn)
    conn.close()

    wb = Workbook()

    # --- Sheet 1: Summary Dashboard ---
    ws = wb.active
    ws.title = "Dashboard"
    ws["A1"] = "Sales Analytics Dashboard"
    ws["A1"].font = Font(name="Arial", bold=True, size=16)
    ws["A2"] = "Generated from sales.db (SQLite) via analysis.py"
    ws["A2"].font = Font(name="Arial", italic=True, size=9)

    next_row = write_df(ws, monthly, start_row=4, title="Monthly Revenue & Profit")
    next_row = write_df(ws, regional, start_row=next_row + 1, title="Regional Performance")

    # Revenue trend line chart
    chart1 = LineChart()
    chart1.title = "Monthly Revenue Trend"
    chart1.style = 10
    chart1.y_axis.title = "Sales"
    chart1.x_axis.title = "Month"
    data = Reference(ws, min_col=2, max_col=3, min_row=4, max_row=4 + len(monthly))
    cats = Reference(ws, min_col=1, min_row=5, max_row=4 + len(monthly))
    chart1.add_data(data, titles_from_data=True)
    chart1.set_categories(cats)
    chart1.width, chart1.height = 18, 9
    ws.add_chart(chart1, "H4")

    # Regional bar chart
    reg_start = next_row - len(regional) - 2
    chart2 = BarChart()
    chart2.title = "Regional Sales vs Profit"
    chart2.y_axis.title = "Amount"
    data2 = Reference(ws, min_col=3, max_col=4, min_row=reg_start, max_row=reg_start + len(regional))
    cats2 = Reference(ws, min_col=1, min_row=reg_start + 1, max_row=reg_start + len(regional))
    chart2.add_data(data2, titles_from_data=True)
    chart2.set_categories(cats2)
    chart2.width, chart2.height = 18, 9
    ws.add_chart(chart2, "H22")

    # --- Sheet 2: Top Products ---
    ws2 = wb.create_sheet("Top Products")
    write_df(ws2, top_prod, title="Top 10 Products by Profit")
    chart3 = BarChart()
    chart3.title = "Top 10 Products by Profit"
    data3 = Reference(ws2, min_col=5, min_row=2, max_row=2 + len(top_prod))
    cats3 = Reference(ws2, min_col=1, min_row=3, max_row=2 + len(top_prod))
    chart3.add_data(data3, titles_from_data=True)
    chart3.set_categories(cats3)
    chart3.width, chart3.height = 18, 10
    ws2.add_chart(chart3, "H2")

    # --- Sheet 3: Customer Recency / Churn Risk ---
    ws3 = wb.create_sheet("Churn Risk")
    at_risk = recency[recency.days_inactive > 180].reset_index(drop=True)
    write_df(ws3, at_risk, title=f"Customers Inactive > 180 Days ({len(at_risk)} of {len(recency)})")

    # --- Sheet 4: RFM Segments ---
    ws4 = wb.create_sheet("RFM Segments")
    write_df(ws4, rfm, title="RFM Segmentation (Quartiles: 1 = Best)")

    # --- Sheet 5: Raw Monthly Category Trend (pivot source) ---
    ws5 = wb.create_sheet("Category Trend")
    cat_trend = an.category_month_trend(an.get_conn())
    pivot = cat_trend.pivot(index="month", columns="category", values="total_sales").fillna(0).reset_index()
    write_df(ws5, pivot, title="Category Sales by Month")

    pie = PieChart()
    pie.title = "Total Sales Share by Category (Latest Snapshot)"
    totals_row = ws5.max_row + 3
    cats_list = list(pivot.columns[1:])
    ws5.cell(row=totals_row, column=1, value="Category")
    ws5.cell(row=totals_row, column=2, value="Total Sales")
    for i, cat in enumerate(cats_list):
        ws5.cell(row=totals_row + 1 + i, column=1, value=cat)
        ws5.cell(row=totals_row + 1 + i, column=2, value=float(pivot[cat].sum()))
    data_pie = Reference(ws5, min_col=2, min_row=totals_row, max_row=totals_row + len(cats_list))
    cats_pie = Reference(ws5, min_col=1, min_row=totals_row + 1, max_row=totals_row + len(cats_list))
    pie.add_data(data_pie, titles_from_data=True)
    pie.set_categories(cats_pie)
    ws5.add_chart(pie, "H2")

    wb.save("sales_report.xlsx")
    print("Saved sales_report.xlsx")


if __name__ == "__main__":
    main()
