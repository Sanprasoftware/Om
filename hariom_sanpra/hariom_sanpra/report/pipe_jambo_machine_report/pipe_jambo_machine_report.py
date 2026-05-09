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
			"fieldname": "pipe_jambo_machine_id",
			"fieldtype": "Link",
			"options": "Pipe Jambo Machine",
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
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 100,
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
		conditions.append(
			"""
			exists (
				select 1
				from `tabOperator Name Items` operator_filter
				where operator_filter.parent = se.name
					and operator_filter.parentfield = 'operator_name'
					and operator_filter.operator_name = %(operator_name)s
			)
			"""
		)
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
		conditions.append("sed.item_code = %(item)s")
		sql_filters["item"] = filters.item

	rows = frappe.db.sql(
		f"""
		select
			se.date,
			se.man_power,
			se.name as pipe_jambo_machine_id,
			(
				select group_concat(
					ifnull(emp.employee_name, operator_item.operator_name)
					order by operator_item.idx
					separator ', '
				)
				from `tabOperator Name Items` operator_item
				left join `tabEmployee` emp on emp.name = operator_item.operator_name
				where operator_item.parent = se.name
					and operator_item.parentfield = 'operator_name'
			) as operator_name,
			se.machine_name as machine_name,
			se.tag_in,
			se.tag_out,
			se.batch as batch_no,
			se.shift,
			sed.item_code,
			it.item_name as item_name,
			sed.qty,
			se.machine_no,
			sed.batch as batch,
			sed.source_warehouse,
			sed.uom,
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
		from `tabPipe Jambo Machine` se
		left join `tabPipe Jambo Items` sed on sed.parent = se.name
		left join `tabItem` it on it.name = sed.item_code
		
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

	last_pipe_jambo_machine_id = None
	for row in rows:
		current_pipe_jambo_machine_id = row.get("pipe_jambo_machine_id")
		if current_pipe_jambo_machine_id== last_pipe_jambo_machine_id:
			row["date"] = ""
			row["pipe_jambo_machine_id"] = ""
			row["operator_name"] = ""
			row["machine_name"] = ""
			row["tag_in"] = ""
			row["tag_out"] = ""
			row["batch_no"] = ""
			row["machine_no"] = ""
			row["shift"] = ""
			row["man_power"] = ""
		else:
			last_pipe_jambo_machine_id = current_pipe_jambo_machine_id

	return rows
