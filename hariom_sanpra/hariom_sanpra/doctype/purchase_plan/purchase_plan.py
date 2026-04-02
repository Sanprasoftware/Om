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

	for index, row in enumerate(doc.get("marketing_order") or [], start=1):
		item_code = row.get("item_code")
		if not item_code:
			continue

		default_bom = frappe.db.get_value("Item", item_code, "default_bom")
		if not default_bom:
			frappe.throw(_("Row {0}: Default BOM not found for item {1}.").format(index, item_code))

		bom_items = frappe.get_all(
			"BOM Item",
			filters={"parent": default_bom, "parenttype": "BOM", "parentfield": "items"},
			fields=["item_code", "qty"],
			order_by="idx asc",
		)

		for bom_item in bom_items:
			if not bom_item.item_code:
				continue

			material_map.setdefault(bom_item.item_code, 0)
			material_map[bom_item.item_code] += flt(bom_item.qty)

	return [
		{
			"item_code": item_code,
			"stock_kg": qty,
		}
		for item_code, qty in material_map.items()
	]
