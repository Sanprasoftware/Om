# # Copyright (c) 2026, Sanpra Software Solution and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _


# def execute(filters: dict | None = None):
# 	filters = frappe._dict(filters or {})
# 	return get_columns(), get_data(filters)


# def get_columns() -> list[dict]:
# 	return [
# 		{
# 			"label": _("Date"),
# 			"fieldname": "posting_date",
# 			"fieldtype": "Date",
# 			"width": 110,
# 		},
# 		{
# 			"label": _("Id"),
# 			"fieldname": "stock_entry_id",
# 			"fieldtype": "Link",
# 			"options": "Stock Entry",
# 			"width": 140,
# 		},
# 		{
# 			"label": _("Operator Name"),
# 			"fieldname": "operator_name",
# 			"fieldtype": "Data",
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Machine Name"),
# 			"fieldname": "machine_name",
# 			"fieldtype": "Link",
# 			"options": "Machine Name",
# 			"width": 150,
# 		},
# 		{
# 			"label": _("TAG IN"),
# 			"fieldname": "custom_tag_in",
# 			"fieldtype": "Data",
# 			"width": 100,
# 		},
# 		{
# 			"label": _("TAG OUT"),
# 			"fieldname": "custom_tag_out",
# 			"fieldtype": "Data",
# 			"width": 100,
# 		},
# 		{
# 			"label": _("BATCH NO"),
# 			"fieldname": "custom_batch_no",
# 			"fieldtype": "Data",
# 			"width": 140,
# 		},
# 		{
# 			"label": _("SHIFT"),
# 			"fieldname": "custom_shift",
# 			"fieldtype": "Link",
# 			"options": "Shift",
# 			"width": 100,
# 		},
# 		{
# 			"label": _("Grade"),
# 			"fieldname": "custom_grade",
# 			"fieldtype": "Data",
# 			"width": 150,
# 		},
# 		{
# 			"label": _("GSM"),
# 			"fieldname": "custom_gsm",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Roll Qty"),
# 			"fieldname": "custom_roll_qty",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Item Code"),
# 			"fieldname": "item_code",
# 			"fieldtype": "Data",
# 			"width": 170,
# 		},
# 		{
# 			"label": _("Item Name"),
# 			"fieldname": "item_name",
# 			"fieldtype": "Data",
# 			"width": 220,
# 		},
# 		{
# 			"label": _("Batch"),
# 			"fieldname": "batch_no",
# 			"fieldtype": "Data",
# 			"width": 220,
# 		},
# 		{
# 			"label": _("Qty"),
# 			"fieldname": "qty",
# 			"fieldtype": "Float",
# 			"width": 100,
# 		},
# 		{
# 			"label": _("Warehouse"),
# 			"fieldname": "warehouse",
# 			"fieldtype": "Link",
# 			"options": "Warehouse",
# 			"width": 180,
# 		},
# 		{
# 			"label": _("Item Type"),
# 			"fieldname": "item_type",
# 			"fieldtype": "Data",
# 			"hidden": 1,
# 		},
# 		{
# 			"label": _("Roll Actual Size Inches"),
# 			"fieldname": "custom_roll_actual_size_inches",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Roll Meter"),
# 			"fieldname": "custom_roll_meter",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Gross Weight"),
# 			"fieldname": "custom_hanging_weight",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Net Weight"),
# 			"fieldname": "custom_net_weight",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Roll SQR Meter"),
# 			"fieldname": "custom_roll_sqr_meter",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 		{
# 			"label": _("Roll Actual GSM"),
# 			"fieldname": "custom_roll_actual_gsm",
# 			"fieldtype": "Float",
# 			"precision": 2,
# 			"width": 150,
# 		},
# 	]


# def get_data(filters: frappe._dict) -> list[dict]:
# 	conditions = ["se.docstatus in (0, 1)"]
# 	conditions.append("se.stock_entry_type = 'GD REWINDING'")
# 	sql_filters: dict[str, str] = {}

# 	if filters.get("from_date"):
# 		conditions.append("se.posting_date >= %(from_date)s")
# 		sql_filters["from_date"] = filters.from_date

# 	if filters.get("to_date"):
# 		conditions.append("se.posting_date <= %(to_date)s")
# 		sql_filters["to_date"] = filters.to_date

# 	if filters.get("id"):
# 		conditions.append("se.name = %(id)s")
# 		sql_filters["id"] = filters.id

# 	if filters.get("operator_name"):
# 		conditions.append("se.custom_operator_name = %(operator_name)s")
# 		sql_filters["operator_name"] = filters.operator_name

# 	if filters.get("machine_name"):
# 		conditions.append("se.custom_machine_name = %(machine_name)s")
# 		sql_filters["machine_name"] = filters.machine_name

# 	if filters.get("custom_shift"):
# 		conditions.append("se.custom_shift = %(custom_shift)s")
# 		sql_filters["custom_shift"] = filters.custom_shift

# 	if filters.get("custom_batch_no"):
# 		conditions.append("se.custom_batch_no = %(custom_batch_no)s")
# 		sql_filters["custom_batch_no"] = filters.custom_batch_no

# 	if filters.get("item"):
# 		conditions.append("sed.item_code = %(item)s")
# 		sql_filters["item"] = filters.item

# 	rows = frappe.db.sql(
# 		f"""
# 		select
# 			se.posting_date,
# 			se.name as stock_entry_id,
# 			ifnull(emp.employee_name, se.custom_operator_name) as operator_name,
# 			se.custom_machine_name as machine_name,
# 			se.custom_tag_in,
# 			se.custom_tag_out,
# 			se.custom_batch_no,
# 			se.custom_qty,
# 			se.custom_shift,
# 			se.custom_grade,
# 			se.custom_gsm,
# 			se.custom_roll_qty,
# 			sed.item_code,
# 			sed.item_name,
# 			sed.qty,
# 			sed.batch_no,
# 			sed.custom_roll_actual_size_inches,
# 			sed.custom_roll_meter,
# 			sed.custom_hanging_weight,
# 			sed.custom_core_weight,
# 			sed.custom_net_weight,
# 			sed.custom_roll_sqr_meter,
# 			sed.custom_roll_actual_gsm,
# 			case
# 				when ifnull(sed.is_finished_item, 0) = 1 then ifnull(sed.t_warehouse, sed.s_warehouse)
# 				else ifnull(sed.s_warehouse, sed.t_warehouse)
# 			end as warehouse,
# 			case
# 				when ifnull(sed.is_scrap_item, 0) = 1 then 'Scrap'
# 				when ifnull(sed.is_finished_item, 0) = 1 then 'Finished'
# 				else 'Raw'
# 			end as item_type
# 		from `tabStock Entry` se
# 		inner join `tabStock Entry Detail` sed on sed.parent = se.name
# 		left join `tabEmployee` emp on emp.name = se.custom_operator_name
# 		where {" and ".join(conditions)}
# 		order by
# 			se.posting_date desc,
# 			se.name desc,
# 			ifnull(sed.is_finished_item, 0) desc,
# 			sed.idx asc
# 		""",
# 		sql_filters,
# 		as_dict=True,
# 	)

# 	last_stock_entry_id = None
# 	for row in rows:
# 		current_stock_entry_id = row.get("stock_entry_id")
# 		if row.get("item_type") != "Raw":
# 			row["custom_grade"] = ""
# 			row["custom_gsm"] = ""
# 			row["custom_roll_qty"] = ""
# 		if current_stock_entry_id == last_stock_entry_id:
# 			row["posting_date"] = ""
# 			row["stock_entry_id"] = ""
# 			row["operator_name"] = ""
# 			row["machine_name"] = ""
# 			row["custom_tag_in"] = ""
# 			row["custom_tag_out"] = ""
# 			row["custom_batch_no"] = ""
# 			row["custom_qty"] = ""
# 			row["custom_shift"] = ""
# 		else:
# 			last_stock_entry_id = current_stock_entry_id

# 	return rows

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
			"width": 110,
		},
		{
			"label": _("Id"),
			"fieldname": "stock_entry_id",
			"fieldtype": "Link",
			"options": "Stock Entry",
			"width": 140,
		},
		{
			"label": _("Operator Name"),
			"fieldname": "operator_name",
			"fieldtype": "Data",
			"width": 220,
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
			"fieldname": "custom_tag_in",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("TAG OUT"),
			"fieldname": "custom_tag_out",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("BATCH NO"),
			"fieldname": "custom_batch_no",
			"fieldtype": "Data",
			"width": 140,
		},
		{
			"label": _("SHIFT"),
			"fieldname": "custom_shift",
			"fieldtype": "Link",
			"options": "Shift",
			"width": 100,
		},
		{
			"label": _("Grade"),
			"fieldname": "custom_grade",
			"fieldtype": "Data",
			"width": 150,
		},
		{
			"label": _("GSM"),
			"fieldname": "custom_gsm",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll Qty"),
			"fieldname": "custom_roll_qty",
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
			"fieldtype": "Data",
			"width": 220,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch_no",
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
			"fieldname": "custom_roll_actual_size_inches",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll Meter"),
			"fieldname": "custom_roll_meter",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Gross Weight"),
			"fieldname": "custom_hanging_weight",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Net Weight"),
			"fieldname": "custom_net_weight",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll SQR Meter"),
			"fieldname": "custom_roll_sqr_meter",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
		{
			"label": _("Roll Actual GSM"),
			"fieldname": "custom_roll_actual_gsm",
			"fieldtype": "Float",
			"precision": 2,
			"width": 150,
		},
	]


def get_data(filters: frappe._dict) -> list[dict]:
	conditions = ["se.docstatus in (0, 1)"]
	conditions.append("se.stock_entry_type = 'GD REWINDING'")

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

	if filters.get("operator_name"):
		conditions.append(
			"""
			exists (
				select 1
				from `tabOperator Name Items` operator_filter
				where operator_filter.parent = se.name
					and operator_filter.parenttype = 'Stock Entry'
					and operator_filter.parentfield = 'custom_operator_name'
					and operator_filter.operator_name = %(operator_name)s
			)
			"""
		)
		sql_filters["operator_name"] = filters.operator_name

	if filters.get("machine_name"):
		conditions.append("se.custom_machine_name = %(machine_name)s")
		sql_filters["machine_name"] = filters.machine_name

	if filters.get("custom_shift"):
		conditions.append("se.custom_shift = %(custom_shift)s")
		sql_filters["custom_shift"] = filters.custom_shift

	if filters.get("custom_batch_no"):
		conditions.append("se.custom_batch_no = %(custom_batch_no)s")
		sql_filters["custom_batch_no"] = filters.custom_batch_no

	if filters.get("item"):
		conditions.append("sed.item_code = %(item)s")
		sql_filters["item"] = filters.item

	rows = frappe.db.sql(
		f"""
			select
				se.posting_date,
				se.name as stock_entry_id,
				(
					select group_concat(
						ifnull(emp.employee_name, operator_item.operator_name)
						order by operator_item.idx
						separator ', '
					)
					from `tabOperator Name Items` operator_item
					left join `tabEmployee` emp
						on emp.name = operator_item.operator_name
					where operator_item.parent = se.name
						and operator_item.parenttype = 'Stock Entry'
						and operator_item.parentfield = 'custom_operator_name'
				) as operator_name,
				se.custom_machine_name as machine_name,
				se.custom_tag_in,
				se.custom_tag_out,
			se.custom_batch_no,
			se.custom_qty,
			se.custom_shift,
			se.custom_grade,
			se.custom_gsm,
			se.custom_roll_qty,

			sed.item_code,
			sed.item_name,
			sed.qty,
			sed.batch_no,

			sed.custom_roll_actual_size_inches,
			sed.custom_roll_meter,
			sed.custom_hanging_weight,
			sed.custom_core_weight,
			sed.custom_net_weight,
			sed.custom_roll_sqr_meter,
			sed.custom_roll_actual_gsm,

			case
				when ifnull(sed.is_finished_item, 0) = 1
					then ifnull(sed.t_warehouse, sed.s_warehouse)
				else ifnull(sed.s_warehouse, sed.t_warehouse)
			end as warehouse,

			case
				when ifnull(sed.is_scrap_item, 0) = 1 then 'Scrap'
				when ifnull(sed.is_finished_item, 0) = 1 then 'Finished'
				else 'Raw'
			end as item_type

		from `tabStock Entry` se

		inner join `tabStock Entry Detail` sed
			on sed.parent = se.name

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

		if row.get("item_type") != "Raw":
			row["custom_grade"] = ""
			row["custom_gsm"] = ""
			row["custom_roll_qty"] = ""

		if current_stock_entry_id == last_stock_entry_id:
			row["posting_date"] = ""
			row["stock_entry_id"] = ""
			# row["operator_name"] = ""
			row["machine_name"] = ""
			row["custom_tag_in"] = ""
			row["custom_tag_out"] = ""
			row["custom_batch_no"] = ""
			row["custom_qty"] = ""
			row["custom_shift"] = ""
		else:
			last_stock_entry_id = current_stock_entry_id

	return rows
