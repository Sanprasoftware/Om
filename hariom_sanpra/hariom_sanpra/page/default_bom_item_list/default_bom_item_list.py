import frappe
from frappe import _
from frappe.utils import cint, flt


@frappe.whitelist()
def get_items(start=0, page_length=50, item_code=None):
	if not frappe.has_permission("Item", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	filters = {
		"disabled": 0,
		"default_bom": ["is", "set"],
	}

	if item_code:
		filters["item_code"] = ["like", f"%{item_code}%"]

	return frappe.get_all(
		"Item",
		filters=filters,
		fields=["name", "item_code", "item_name", "stock_uom", "default_bom"],
		order_by="item_code asc",
		start=cint(start),
		page_length=cint(page_length),
	)


@frappe.whitelist()
def get_boms(item_code):
	if not frappe.has_permission("BOM", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	default_bom = frappe.db.get_value("Item", item_code, "default_bom")
	boms = frappe.get_all(
		"BOM",
		filters={"item": item_code},
		fields=[
			"name",
			"item",
			"item_name",
			"company",
			"quantity",
			"uom",
			"docstatus",
			"is_active",
			"is_default",
			"is_phantom_bom",
			"track_semi_finished_goods",
		],
		order_by="is_default desc, modified desc",
	)

	for bom in boms:
		bom["is_default"] = 1 if bom.name == default_bom else bom.is_default

	return boms


@frappe.whitelist()
def get_bom_items(bom_no):
	if not frappe.has_permission("BOM", "read", bom_no):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	bom = frappe.db.get_value(
		"BOM",
		bom_no,
		["name", "item", "item_name", "company", "quantity", "uom", "docstatus", "is_active", "is_phantom_bom", "track_semi_finished_goods"],
		as_dict=True,
	)

	if not bom:
		frappe.throw(_("BOM {0} not found").format(bom_no))

	items = frappe.get_all(
		"BOM Item",
		filters={"parent": bom_no, "parenttype": "BOM", "parentfield": "items"},
		fields=["idx", "item_code", "item_name", "qty", "uom", "stock_qty", "stock_uom", "bom_no"],
		order_by="idx asc",
	)

	return {"bom": bom, "items": items}


@frappe.whitelist()
def make_work_order(bom_no, item, qty=1, company=None, use_multi_level_bom=0):
	from erpnext.manufacturing.doctype.work_order.work_order import make_work_order as make_erpnext_work_order

	if not frappe.has_permission("Work Order", "write"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	bom = frappe.db.get_value(
		"BOM",
		bom_no,
		["item", "company", "docstatus", "is_active", "is_phantom_bom", "track_semi_finished_goods"],
		as_dict=True,
	)

	if not bom:
		frappe.throw(_("BOM {0} not found").format(bom_no))

	if bom.docstatus != 1 or not bom.is_active:
		frappe.throw(_("Only active submitted BOM can be used to create a Work Order."))

	if bom.is_phantom_bom:
		frappe.throw(_("Work Order cannot be created for a Phantom BOM."))

	if item != bom.item:
		frappe.throw(_("Item {0} does not match BOM item {1}.").format(item, bom.item))

	doc = make_erpnext_work_order(
		bom_no=bom_no,
		item=item,
		qty=flt(qty) or 1,
		company=company or bom.company,
		use_multi_level_bom=0 if bom.track_semi_finished_goods else use_multi_level_bom,
	)

	return doc.as_dict()
