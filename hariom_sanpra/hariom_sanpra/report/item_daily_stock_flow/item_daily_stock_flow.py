# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	validate_filters(filters)
	return get_columns(), get_data(filters)


def validate_filters(filters):
	if not filters.get("company"):
		frappe.throw(_("Company is required"))

	if not filters.get("date"):
		frappe.throw(_("Date is required"))


def get_data(filters):
	filters = frappe._dict(filters)
	filters.date = getdate(filters.date)

	opening_by_item_warehouse = get_opening_qty_by_item_warehouse(filters)
	movement_by_item_warehouse = get_movement_by_item_warehouse(filters)
	item_details = get_item_details(opening_by_item_warehouse, movement_by_item_warehouse)
	item_warehouse_keys = get_item_warehouse_keys(opening_by_item_warehouse, movement_by_item_warehouse)

	if not item_warehouse_keys:
		return []

	rows = []

	for item_code, warehouse in sorted(item_warehouse_keys):
		item_info = item_details[item_code]
		running_opening = opening_by_item_warehouse.get((item_code, warehouse), 0.0)
		day_data = movement_by_item_warehouse.get((item_code, warehouse), {})
		in_qty = day_data.get("in_qty", 0.0)
		out_qty = day_data.get("out_qty", 0.0)
		closing_qty = running_opening + in_qty - out_qty

		rows.append(
			{
				"report_date": filters.date,
				"item_code": item_code,
				"item_name": item_info.get("item_name"),
				"warehouse": warehouse,
				"stock_uom": item_info.get("stock_uom"),
				"opening_qty": running_opening,
				"in_qty": in_qty,
				"out_qty": out_qty,
				"closing_qty": closing_qty,
			}
		)

	return rows


def get_opening_qty_by_item_warehouse(filters):
	conditions = [
		"sle.docstatus < 2",
		"sle.is_cancelled = 0",
		"sle.company = %(company)s",
		"sle.posting_date < %(date)s",
	]

	if filters.get("item_code"):
		conditions.append("sle.item_code = %(item_code)s")
	if filters.get("warehouse"):
		conditions.append("sle.warehouse = %(warehouse)s")

	rows = frappe.db.sql(
		f"""
		select
			sle.item_code,
			sle.warehouse,
			sum(sle.actual_qty) as opening_qty
		from `tabStock Ledger Entry` sle
		where {' and '.join(conditions)}
		group by sle.item_code, sle.warehouse
		""",
		filters,
		as_dict=True,
	)

	return {(row.item_code, row.warehouse): row.opening_qty or 0.0 for row in rows}


def get_movement_by_item_warehouse(filters):
	conditions = [
		"sle.docstatus < 2",
		"sle.is_cancelled = 0",
		"sle.company = %(company)s",
		"sle.posting_date = %(date)s",
	]

	if filters.get("item_code"):
		conditions.append("sle.item_code = %(item_code)s")
	if filters.get("warehouse"):
		conditions.append("sle.warehouse = %(warehouse)s")

	rows = frappe.db.sql(
		f"""
		select
			sle.item_code,
			sle.warehouse,
			sum(
				case
					when sle.actual_qty > 0
						and sle.voucher_type in ('Purchase Receipt', 'Stock Entry', 'Stock Reconciliation')
					then sle.actual_qty
					else 0
				end
			) as in_qty,
			sum(
				case
					when sle.actual_qty < 0
						and sle.voucher_type in ('Delivery Note', 'Stock Entry', 'Stock Reconciliation')
					then abs(sle.actual_qty)
					else 0
				end
			) as out_qty
		from `tabStock Ledger Entry` sle
		where {' and '.join(conditions)}
		group by sle.item_code, sle.warehouse
		""",
		filters,
		as_dict=True,
	)

	movement_map = {}
	for row in rows:
		movement_map[(row.item_code, row.warehouse)] = {
			"in_qty": row.in_qty or 0.0,
			"out_qty": row.out_qty or 0.0,
		}

	return movement_map


def get_item_details(opening_by_item_warehouse, movement_by_item_warehouse):
	item_codes = {item_code for item_code, _ in opening_by_item_warehouse}
	item_codes.update(item_code for item_code, _ in movement_by_item_warehouse)

	if not item_codes:
		return {}

	rows = frappe.get_all(
		"Item",
		filters={"name": ["in", list(item_codes)]},
		fields=["name", "item_name", "stock_uom"],
	)

	return {row.name: row for row in rows}


def get_item_warehouse_keys(opening_by_item_warehouse, movement_by_item_warehouse):
	item_warehouse_keys = set(opening_by_item_warehouse)
	item_warehouse_keys.update((item_code, warehouse) for item_code, warehouse in movement_by_item_warehouse)
	return item_warehouse_keys


def get_columns():
	return [
		{
			"label": _("Date"),
			"fieldname": "report_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 180,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 160,
		},
		{
			"label": _("UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 80,
		},
		{
			"label": _("Opening Qty"),
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
			"label": _("Closing Qty"),
			"fieldname": "closing_qty",
			"fieldtype": "Float",
			"width": 120,
		},
	]
