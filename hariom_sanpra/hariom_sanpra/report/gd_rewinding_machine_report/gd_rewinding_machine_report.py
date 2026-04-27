# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	filters = frappe._dict(filters or {})
	return get_columns(),get_data(filters)


def get_columns() -> list[dict]:
	return [
		{
			"label": _("Date"),
			"fieldname": "date", 
			"fieldtype": "Date",
			"width": 110,
		},
		{
			"label": _("Id"),
			"fieldname": "gd_rewinding_id",
			"fieldtype": "Link",
			"options": "GD Rewinding",
			"width": 140,
		},
		{
			"label": _("Operator Name"),
			"fieldname": "operator_name",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Machine Name"),
			"fieldname": "machine_name",
			"fieldtype": "Link",
			"options": "Machine Name",
			"width": 150,
		},
		{
			"label": _("TAG IN"),
			"fieldname": "tag_in",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("TAG OUT"),
			"fieldname": "tag_out",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("BATCH NO"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch No",
			"width": 140,
		},
		{
			"label": _("Machine No"),
			"fieldname": "machine_no",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("SHIFT"),
			"fieldname": "shift",
			"fieldtype": "Link",
			"options": "Shift",
			"width": 100,
		},
		{
			"label": _("Grade"),
			"fieldname": "grade",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("GSM"),
			"fieldname": "gsm",
			"fieldtype": "Int",
			"width": 150,
		},
		{
			"label": _("Roll Qty"),
			"fieldname": "roll_qty",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 170,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Link",
			"options": "Item",
			"width": 220,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 220,
		},
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 180,
		},
		{
			"label": _("Item Type"),
			"fieldname": "item_type",
			"fieldtype": "Data",
			"hidden": 1,
		},
		{
			"label": _("Roll Actual Size Inches"),
			"fieldname": "roll_actual_size_inches",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll Meter"),
			"fieldname": "roll_meter",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Gross Weight"),
			"fieldname": "gross_weight",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Net Weight"),
			"fieldname": "net_weight",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll SQR Meter"),
			"fieldname": "roll_sqr_meter",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll Actual GSM"),
			"fieldname": "roll_actual_gsm",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
	]


def get_data(filters: frappe._dict) -> list[dict]:
	conditions = ["se.docstatus in (0, 1)"]
	sql_filters: dict[str, str] = {}

	if filters.get("from_date"):
		conditions.append("se.date >= %(from_date)s")
		sql_filters["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("se.date <= %(to_date)s")
		sql_filters["to_date"] = filters.to_date

	if filters.get("id"):
		conditions.append("se.name = %(id)s")
		sql_filters["id"] = filters.id

	if filters.get("operator_name"):
		conditions.append("se.operator_name = %(operator_name)s")
		sql_filters["operator_name"] = filters.operator_name

	if filters.get("machine_name"):
		conditions.append("se.machine_name = %(machine_name)s")
		sql_filters["machine_name"] = filters.machine_name

	if filters.get("shift"):
		conditions.append("se.shift = %(shift)s")
		sql_filters["shift"] = filters.shift

	if filters.get("batch_no"):
		conditions.append("se.batch_no = %(batch_no)s")
		sql_filters["batch_no"] = filters.batch_no

	if filters.get("item"):
		conditions.append("sed.item_code = %(item)s")
		sql_filters["item"] = filters.item

	rows = frappe.db.sql(
		f"""
		select
			se.date,
			se.name as gd_rewinding_id,
			ifnull(emp.employee_name, se.operator_name) as operator_name,
			se.machine_name as machine_name,
			se.tag_in,
			se.tag_out,
			se.batch as batch_no,
			se.machine_no,
			se.shift,
			sed.grade,
			sed.gsm,
			sed.roll_qty,
			sed.item_code,
			# se.quantity,
			it.item_name as item_name,
			# sed.hanging_weight,
			sed.qty,
			sed.batch as batch,
			sed.roll_actual_size as roll_actual_size_inches,
			sed.roll_meter,
			sed.core_weight,
			sed.net_weight,
			sed.gross_weight,
			sed.roll_sqr_meter,
			sed.roll_actual_gsm,
			sed.source_warehouse,
			case
				when ifnull(sed.is_finished_item, 0) = 1 then ifnull(sed.target_warehouse, sed.source_warehouse)
				else ifnull(sed.source_warehouse, sed.target_warehouse)
			end as warehouse,
			case
				when ifnull(sed.is_scrap_item, 0) = 1 then 'Scrap'
				when ifnull(sed.is_finished_item, 0) = 1 then 'Finished'
				else 'Raw'
			end as item_type
		from `tabGD Rewinding` se
		inner join `tabGD Rewinding Child` sed on sed.parent = se.name
		left join `tabEmployee` emp on emp.name = se.operator_name
		left join `tabItem` it on it.name = sed.item_code
		
		where {" and ".join(conditions)}
		order by
			se.date desc,
			se.name desc,
			ifnull(sed.is_finished_item, 0) desc,
			sed.idx asc
		""",
		sql_filters,
		as_dict=True,
	)

	last_gd_rewinding_id = None
	for row in rows:
		current_gd_rewinding_id = row.get("gd_rewinding_id")
		if row.get("warehouse") != row.get("source_warehouse"):
			row["gsm"] = ""
			row["roll_qty"] = ""
			row["grade"] = ""
		row.pop("source_warehouse", None)
		if current_gd_rewinding_id == last_gd_rewinding_id:
			row["date"] = ""
			row["gd_rewinding_id"] = ""
			row["operator_name"] = ""
			row["machine_name"] = ""
			row["tag_in"] = ""
			row["tag_out"] = ""
			row["batch_no"] = ""
			row["qty"] = ""
			row["machine_no"] = ""
			row["shift"] = ""
		else:
			last_gd_rewinding_id = current_gd_rewinding_id

	return rows
