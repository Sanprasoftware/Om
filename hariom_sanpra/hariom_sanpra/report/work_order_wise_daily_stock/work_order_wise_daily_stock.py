# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)
	return get_columns(), get_data(filters)


def validate_filters(filters):
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	if not filters.get("work_order"):
		frappe.throw(_("Work Order is required"))

	if not filters.get("date"):
		frappe.throw(_("Date is required"))



def get_data(filters):
	item_codes = get_work_order_item_codes(filters.work_order)
	if not item_codes:
		return []

	conditions = ["sle.docstatus < 2", "sle.is_cancelled = 0", "sle.company = %(company)s", "sle.posting_date <= %(date)s"]
	sle_params = dict(filters)
	sle_params["item_codes"] = tuple(item_codes)
	conditions.append("sle.item_code in %(item_codes)s")

	rows = frappe.db.sql(
		f"""
		select
			%(work_order)s as work_order,
			%(date)s as report_date,
			sle.item_code,
			max(item.stock_uom) as stock_uom,
			sum(case when sle.posting_date < %(date)s then sle.actual_qty else 0 end) as opening_qty,
			sum(case when sle.posting_date = %(date)s and sle.actual_qty > 0 then sle.actual_qty else 0 end) as in_qty,
			sum(case when sle.posting_date = %(date)s and sle.actual_qty < 0 then abs(sle.actual_qty) else 0 end) as out_qty,
			sum(case when sle.posting_date = %(date)s then sle.actual_qty else 0 end) as balance_qty,
			sum(sle.actual_qty) as closing_qty
		from `tabStock Ledger Entry` sle
		inner join `tabItem` item on item.name = sle.item_code
		where {' and '.join(conditions)}
		group by sle.item_code
		order by sle.item_code
		""",
		sle_params,
		as_dict=True,
	)

	stock_by_item = {row.item_code: row for row in rows}
	item_uom_map = get_item_uom_map(item_codes)
	data = []
	for item_code in sorted(item_codes):
		row = stock_by_item.get(item_code, frappe._dict())
		opening_qty = row.get("opening_qty", 0.0) or 0.0
		in_qty = row.get("in_qty", 0.0) or 0.0
		out_qty = row.get("out_qty", 0.0) or 0.0
		balance_qty = in_qty - out_qty
		closing_qty = opening_qty + balance_qty

		data.append(
			{
				"work_order": filters.work_order,
				"report_date": filters.date,
				"item_code": item_code,
				"stock_uom": row.get("stock_uom") or item_uom_map.get(item_code),
				"opening_qty": opening_qty,
				"in_qty": in_qty,
				"out_qty": out_qty,
				"balance_qty": balance_qty,
				"closing_qty": closing_qty,
			}
		)

	return data


def get_work_order_item_codes(work_order):
	item_codes = [
		row.item_code
		for row in frappe.get_all(
			"Work Order Item",
			filters={"parent": work_order, "parenttype": "Work Order"},
			fields=["item_code"],
			order_by="idx asc",
		)
		if row.item_code
	]
	return list(dict.fromkeys(item_codes))


def get_item_uom_map(item_codes):
	if not item_codes:
		return {}

	rows = frappe.get_all("Item", filters={"name": ["in", item_codes]}, fields=["name", "stock_uom"])
	return {row.name: row.stock_uom for row in rows}



def get_columns():
	return [
		{
			"label": _("Work Order"),
			"fieldname": "work_order",
			"fieldtype": "Link",
			"options": "Work Order",
			"width": 140,
		},
		{
			"label": _("Date"),
			"fieldname": "report_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Opening Stock"),
			"fieldname": "opening_qty",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("In Qty"),
			"fieldname": "in_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Out Qty"),
			"fieldname": "out_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Balance"),
			"fieldname": "balance_qty",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Closing Stock"),
			"fieldname": "closing_qty",
			"fieldtype": "Float",
			"width": 120,
		},
	]
