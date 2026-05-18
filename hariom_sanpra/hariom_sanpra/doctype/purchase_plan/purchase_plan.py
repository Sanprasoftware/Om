# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class PurchasePlan(Document):
	pass


@frappe.whitelist()
def get_purchase_plan_materials(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)

	material_map = {}
	skipped_rows = []

	for index, row in enumerate(doc.get("marketing_order") or [], start=1):
		item_code = row.get("item_code")
		if not item_code:
			continue

		default_bom = get_default_bom(item_code)
		if not default_bom:
			skipped_rows.append(_("Row {0}: Default BOM not found for item {1}.").format(index, item_code))
			continue

		bom_qty = flt(frappe.db.get_value("BOM", default_bom, "quantity"))
		if not bom_qty:
			skipped_rows.append(_("Row {0}: BOM quantity is zero for item {1}.").format(index, item_code))
			continue

		bom_items = frappe.get_all(
			"BOM Item",
			filters={"parent": default_bom, "parenttype": "BOM", "parentfield": "items"},
			fields=["item_code", "qty", "stock_qty"],
			order_by="idx asc",
		)
		required_fg_qty = flt(row.get("qty_kg"))
		if flt(row.get("wastage")):
			required_fg_qty += required_fg_qty * flt(row.get("wastage")) / 100

		for bom_item in bom_items:
			if not bom_item.item_code:
				continue

			material_map.setdefault(bom_item.item_code, 0)
			material_map[bom_item.item_code] += (flt(bom_item.stock_qty) or flt(bom_item.qty)) * required_fg_qty / bom_qty

	if skipped_rows:
		frappe.msgprint("<br>".join(skipped_rows), title=_("Skipped Purchase Plan Rows"), indicator="orange")

	stock_map = get_actual_stock(material_map.keys())

	return [
		{
			"item_code": item_code,
			"stock_kg": stock_map.get(item_code, 0),
			"required_stock": required_stock,
			"shortage_qty": max(required_stock - stock_map.get(item_code, 0), 0),
			"purchase": "YES" if required_stock > stock_map.get(item_code, 0) else "NO",
		}
		for item_code, required_stock in material_map.items()
	]


def get_default_bom(item_code):
	default_bom = frappe.db.get_value("Item", item_code, "default_bom")
	if default_bom:
		return default_bom

	bom = frappe.db.get_value(
		"BOM",
		{"item": item_code, "is_active": 1, "docstatus": 1},
		"name",
		order_by="is_default desc, modified desc",
	)
	return bom


def get_actual_stock(item_codes):
	stock_map = {}
	item_codes = list(item_codes)
	if not item_codes:
		return stock_map

	for row in frappe.get_all(
		"Bin",
		filters={"item_code": ["in", item_codes]},
		fields=["item_code", "actual_qty"],
	):
		stock_map.setdefault(row.item_code, 0)
		stock_map[row.item_code] += flt(row.actual_qty)

	return stock_map
