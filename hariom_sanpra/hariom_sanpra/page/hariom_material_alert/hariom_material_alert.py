import frappe
from frappe import _
from frappe.utils import cint, flt
from frappe.utils.nestedset import get_descendants_of


@frappe.whitelist()
def get_material_stock(company=None, warehouse=None, item_group=None, consumption_days=30):
	"""Return available stock and consumption cover grouped by Item Group and UOM."""
	if not frappe.has_permission("Item", "read") or not frappe.has_permission("Stock Ledger Entry", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	company = company or frappe.defaults.get_user_default("Company")
	consumption_days = max(cint(consumption_days), 1)
	conditions = ["item.disabled = 0"]
	values = {"consumption_days": consumption_days}

	if company:
		conditions.append("warehouse.company = %(company)s")
		values["company"] = company
	if warehouse:
		warehouses = [warehouse, *get_descendants_of("Warehouse", warehouse, ignore_permissions=True)]
		conditions.append("stock.warehouse IN %(warehouses)s")
		values["warehouses"] = warehouses
	raw_material_group = frappe.db.get_value(
		"Item Group", "Raw Material", ["lft", "rgt"], as_dict=True
	)
	if not raw_material_group:
		frappe.throw(_("Item Group Raw Material was not found"))

	item_group = item_group or "Raw Material"
	if item_group:
		group = frappe.db.get_value("Item Group", item_group, ["lft", "rgt"], as_dict=True)
		if not group:
			frappe.throw(_("Item Group {0} was not found").format(item_group))
		if group.lft < raw_material_group.lft or group.rgt > raw_material_group.rgt:
			frappe.throw(_("Please select Raw Material or one of its child Item Groups."))
		conditions.append(
			"item_group.lft >= %(group_lft)s AND item_group.rgt <= %(group_rgt)s"
		)
		values.update(group_lft=group.lft, group_rgt=group.rgt)

	rows = frappe.db.sql(
		f"""
		SELECT
			item.item_group,
			item.stock_uom,
			SUM(stock.actual_qty) AS actual_qty,
			SUM(COALESCE(bin.projected_qty, stock.actual_qty)) AS projected_qty,
			COUNT(DISTINCT stock.item_code) AS item_count,
			COALESCE(SUM(consumption.consumed_qty), 0) AS consumed_qty
		FROM (
			SELECT item_code, warehouse, SUM(actual_qty) AS actual_qty
			FROM `tabStock Ledger Entry`
			WHERE docstatus < 2
				AND is_cancelled = 0
				AND posting_date <= CURDATE()
			GROUP BY item_code, warehouse
		) stock
		INNER JOIN `tabItem` item ON item.name = stock.item_code
		INNER JOIN `tabItem Group` item_group ON item_group.name = item.item_group
		INNER JOIN `tabWarehouse` warehouse ON warehouse.name = stock.warehouse
		LEFT JOIN `tabBin` bin
			ON bin.item_code = stock.item_code AND bin.warehouse = stock.warehouse
		LEFT JOIN (
			SELECT item_code, warehouse, SUM(ABS(actual_qty)) AS consumed_qty
			FROM `tabStock Ledger Entry`
			WHERE docstatus < 2
				AND is_cancelled = 0
				AND actual_qty < 0
				AND posting_date >= DATE_SUB(CURDATE(), INTERVAL %(consumption_days)s DAY)
				AND posting_date <= CURDATE()
			GROUP BY item_code, warehouse
		) consumption
			ON consumption.item_code = stock.item_code AND consumption.warehouse = stock.warehouse
		WHERE {' AND '.join(conditions)}
		GROUP BY item.item_group, item.stock_uom
		HAVING ABS(actual_qty) > 0.000001 OR consumed_qty > 0.000001
		ORDER BY item.item_group, item.stock_uom
		""",
		values,
		as_dict=True,
	)

	for row in rows:
		row.actual_qty = flt(row.actual_qty)
		row.projected_qty = flt(row.projected_qty)
		row.consumed_qty = flt(row.consumed_qty)
		daily_consumption = row.consumed_qty / consumption_days
		row.days_left = max(row.actual_qty, 0) / daily_consumption if daily_consumption else None
		if row.actual_qty <= 0 or (row.days_left is not None and row.days_left <= 3):
			row.status = "danger"
		elif row.days_left is not None and row.days_left <= 10:
			row.status = "warning"
		else:
			row.status = "safe"

	return rows


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_raw_material_item_groups(doctype, txt, searchfield, start, page_len, filters):
	"""Link-field options limited to Raw Material and all of its descendants."""
	if not frappe.has_permission("Item Group", "read"):
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	raw_material_group = frappe.db.get_value(
		"Item Group", "Raw Material", ["lft", "rgt"], as_dict=True
	)
	if not raw_material_group:
		return []

	return frappe.db.sql(
		"""
		SELECT name
		FROM `tabItem Group`
		WHERE lft >= %(lft)s
			AND rgt <= %(rgt)s
			AND name LIKE %(txt)s
		ORDER BY lft
		LIMIT %(start)s, %(page_len)s
		""",
		{
			"lft": raw_material_group.lft,
			"rgt": raw_material_group.rgt,
			"txt": f"%{txt}%",
			"start": cint(start),
			"page_len": cint(page_len),
		},
	)
