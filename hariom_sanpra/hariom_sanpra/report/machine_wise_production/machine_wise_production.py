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
			"fieldname": "posting_date",
			"fieldtype": "Date",
			"width": 100,
		},
		{
			"label": _("Id"),
			"fieldname": "stock_entry_id",
			"fieldtype": "Link",
			"options": "Stock Entry",
			"width": 170,
		},
		{
			"label": _("Stock Entry Type"),
			"fieldname": "stock_entry_type",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("Operator Name"),
			"fieldname": "operator_name",
			"fieldtype": "Link",
			"options": "Operator Name",
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
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Data",
			"width": 170,
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
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
			"width": 200,
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
		conditions.append("se.posting_date >= %(from_date)s")
		sql_filters["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("se.posting_date <= %(to_date)s")
		sql_filters["to_date"] = filters.to_date

	if filters.get("id"):
		conditions.append("se.name = %(id)s")
		sql_filters["id"] = filters.id

	if filters.get("machine_name"):
		conditions.append("se.custom_machine_name = %(machine_name)s")
		sql_filters["machine_name"] = filters.machine_name

	rows = frappe.db.sql(
		f"""
		select
			se.posting_date,
			se.name as stock_entry_id,
			se.stock_entry_type,
			(
				select group_concat(
					ifnull(emp.employee_name, operator_item.operator_name)
					order by operator_item.idx
					separator ', '
				)
				from `tabOperator Name Items` operator_item
				left join `tabEmployee` emp on emp.name = operator_item.operator_name
				where operator_item.parent = se.name
					and operator_item.parentfield = 'custom_operator_name'
			) as operator_name,
			se.custom_machine_name as machine_name,
			sed.item_code,
			sed.item_name,
			sed.qty,
			case
				when ifnull(sed.is_finished_item, 0) = 1 then ifnull(sed.t_warehouse, sed.s_warehouse)
				else ifnull(sed.s_warehouse, sed.t_warehouse)
			end as warehouse,
			case
				when ifnull(sed.is_finished_item, 0) = 1 then 'Finished'
				else 'Raw'
			end as item_type
		from `tabStock Entry` se
		inner join `tabStock Entry Detail` sed on sed.parent = se.name
		where {" and ".join(conditions)}
		order by
			se.posting_date desc,
			se.name desc,
			ifnull(sed.is_finished_item, 0) desc,
			sed.idx asc
		""",
		sql_filters,
		as_dict=True,
	)

	last_stock_entry_id = None
	for row in rows:
		current_stock_entry_id = row.get("stock_entry_id")
		if current_stock_entry_id == last_stock_entry_id:
			row["posting_date"] = ""
			row["stock_entry_id"] = ""
			row["stock_entry_type"] = ""
			row["operator_name"] = ""
			row["machine_name"] = ""
		else:
			last_stock_entry_id = current_stock_entry_id

	return rows
