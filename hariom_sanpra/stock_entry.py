import frappe
from frappe.utils import flt


@frappe.whitelist()
def get_scrap_items_for_qty(bom_no, company, qty, work_order=None, job_card=None):
	if not bom_no or not company or not qty:
		return []

	se = frappe.new_doc("Stock Entry")
	se.company = company
	se.bom_no = bom_no
	se.work_order = work_order
	se.job_card = job_card

	if work_order:
		se.set_work_order_details()

	item_dict = se.get_bom_scrap_material(flt(qty)) or {}

	if getattr(se, "pro_doc", None) and se.pro_doc.scrap_warehouse:
		for item in item_dict.values():
			item["to_warehouse"] = se.pro_doc.scrap_warehouse

	items = []
	for item_code, item in item_dict.items():
		items.append(
			{
				"item_code": item.get("item_code") or item_code,
				"qty": flt(item.get("qty")),
				"uom": item.get("uom"),
				"stock_uom": item.get("stock_uom"),
				"conversion_factor": flt(item.get("conversion_factor") or 1),
				"description": item.get("description"),
				"item_name": item.get("item_name"),
				"from_warehouse": item.get("from_warehouse"),
				"to_warehouse": item.get("to_warehouse"),
			}
		)

	return items
