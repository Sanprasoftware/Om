# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	filters = frappe._dict(filters or {})
	return get_columns(), get_data(filters)


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
			"fieldname": "rk_slitting_machine_id",
			"fieldtype": "Link",
			"options": "RK Slitting Machine",
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
			"label": _("Man Power"),
			"fieldname": "man_power",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Machine Speed"),
			"fieldname": "machine_speed",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Roll Slitting Width (MM)"),
			"fieldname": "roll_slitting_width_mm",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("No. of Coils (UPS)"),
			"fieldname": "no_of_coils_ups",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Roll Slitting Width (GP)"),
			"fieldname": "roll_slitting_width_gp",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"label": _("Trim Wastage (mm)"),
			"fieldname": "trim_wastage_mm",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": _("Item Code"),
			"fieldname": "item",
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
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Data",
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
			"label": _("Line MTR"),
			"fieldname": "line_mtr",
			"fieldtype": "Float",
			"width": 180,
		},
		{
			"label": _("MTR Length"),
			"fieldname": "mtr_length",
			"fieldtype": "Float",
			"width": 180,
			
		},
		{
			"label": _("Trim KG"),
			"fieldname": "trim_kg",
			"fieldtype": "Float",
			"width": 180,
		},
		{
			"label": _("Output Coil (Nos)"),
			"fieldname": "output_coil_nos",
			"fieldtype": "Int",
			"width": 180,
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
		conditions.append("se.batch = %(batch_no)s")
		sql_filters["batch_no"] = filters.batch_no

	if filters.get("item"):
		conditions.append("sed.item = %(item)s")
		sql_filters["item"] = filters.item

	rows = frappe.db.sql(
		f"""
		select
			se.date,
			se.man_power,
			se.machine_speed,
			se.name as rk_slitting_machine_id,
			ifnull(emp.employee_name, se.operator_name) as operator_name,
			se.machine_name as machine_name,
			se.tag_in,
			se.tag_out,
			se.batch as batch_no,
			se.shift,
			se.roll_slitting_width_mm,
			se.no_of_coils_ups,
			sed.item,
			it.item_name as item_name,
			sed.qty,
			se.machine_no,
			se.roll_slitting_width_gp,
			se.trim_wastage_mm,
			sed.batch_no as batch,
			sed.source_warehouse,
			sed.uom,
			sed.line_mtr,
			sed.mtr_length,
			sed.trim_kg,
			sed.output_coil_nos,
			case
				when ifnull(sed.is_finished_item, 0) = 1 then ifnull(sed.target_warehouse, sed.source_warehouse)
				else ifnull(sed.source_warehouse, sed.target_warehouse)
			end as warehouse,
			case
				when sed.name is null then ''
				when ifnull(sed.is_scrap_item, 0) = 1 then 'Scrap'
				when ifnull(sed.is_finished_item, 0) = 1 then 'Finished'
				else 'Raw'
			end as item_type
		from `tabRK Slitting Machine` se
		left join `tabRK Slitting Machine Items` sed on sed.parent = se.name
		left join `tabEmployee` emp on emp.name = se.operator_name
		left join `tabItem` it on it.name = sed.item
		
		where {" and ".join(conditions)}
		order by
			se.date desc,
			se.name desc,
			case
				when ifnull(sed.is_finished_item, 0) = 1 then 1
				when ifnull(sed.is_scrap_item, 0) = 1 then 3
				else 2
			end asc,
			sed.idx asc
		""",
		sql_filters,
		as_dict=True,
	)

	last_rk_slitting_machine_id = None
	for row in rows:
		current_rk_slitting_machine_id = row.get("rk_slitting_machine_id")
		if current_rk_slitting_machine_id == last_rk_slitting_machine_id:
			row["date"] = ""
			row["rk_slitting_machine_id"] = ""
			row["operator_name"] = ""
			row["machine_name"] = ""
			row["tag_in"] = ""
			row["tag_out"] = ""
			row["batch_no"] = ""
			row["machine_no"] = ""
			row["shift"] = ""
			row["man_power"] = ""
			row["machine_speed"] = ""
			row["roll_slitting_width_mm"] = ""
			row["no_of_coils_ups"] = ""
			row["roll_slitting_width_gp"] = ""
			row["trim_wastage_mm"] = ""
		else:
			last_rk_slitting_machine_id = current_rk_slitting_machine_id

	return rows
