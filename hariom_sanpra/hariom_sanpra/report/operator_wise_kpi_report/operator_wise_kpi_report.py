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
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 170,
		},
		{
			"label": _("Feet"),
			"fieldname": "feet",
			"fieldtype": "Link",
			"options": "FEET",
			"width": 100,
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
			"label": _("Work Order Qty"),
			"fieldname": "work_order_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Variation"),
			"fieldname": "variation",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Variation %"),
			"fieldname": "variation_percentage",
			"fieldtype": "Percent",
			"width": 120,
		},
		# {
		# 	"label": _("GSM"),
		# 	"fieldname": "gsm",
		# 	"fieldtype": "Link",
		# 	"options": "GSM",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("METER"),
		# 	"fieldname": "meter",
		# 	"fieldtype": "Link",
		# 	"options": "Meter",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("ROLL"),
		# 	"fieldname": "roll",
		# 	"fieldtype": "Link",
		# 	"options": "Roll",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("COLOUR"),
		# 	"fieldname": "colour",
		# 	"fieldtype": "Link",
		# 	"options": "Colour",
		# 	"width": 100,
		# },
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
			"label": _("Wastage"),
			"fieldname": "wastage",
			"fieldtype": "Float",
			"width": 100,
		},
	]


def get_data(filters: frappe._dict) -> list[dict]:
	conditions = [
		"se.docstatus in (0, 1)",
		# "(ifnull(sed.is_finished_item, 0) = 1 OR ifnull(sed.is_scrap_item, 0) = 1)",
	]
	if filters.get("is_finished_item") and not filters.get("is_scrap_item"):
		conditions.append("ifnull(sed.is_finished_item, 0) = 1")

	elif filters.get("is_scrap_item") and not filters.get("is_finished_item"):
		conditions.append("ifnull(sed.is_scrap_item, 0) = 1")

	else:
		# Dono unchecked ya dono checked -> existing behavior
		conditions.append(
			"(ifnull(sed.is_finished_item, 0) = 1 OR ifnull(sed.is_scrap_item, 0) = 1)"
		)
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
	
	if filters.get("feet"):
		conditions.append("item.custom_feet = %(feet)s")
		sql_filters["feet"] = filters.feet

	if filters.get("report_based_on") == "BOM Wise":
		conditions.append("""
			EXISTS (
				SELECT 1
				FROM `tabStock Entry Type` setype
				WHERE setype.name = se.stock_entry_type
				AND setype.purpose = 'Manufacture'
			)
		""")
	
	warehouse_expression = """
	case
		when ifnull(sed.is_finished_item, 0) = 1	
			then ifnull(sed.t_warehouse, sed.s_warehouse)
		else
			ifnull(sed.s_warehouse, sed.t_warehouse)
	end
	"""

	if filters.get("warehouse"):
		conditions.append(f"{warehouse_expression} = %(warehouse)s")
		sql_filters["warehouse"] = filters.warehouse
  
	if filters.get("manufacturing_type"):
			conditions.append("se.custom_manufacture_type = %(manufacturing_type)s")
			sql_filters["manufacturing_type"] = filters.manufacturing_type

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
			se.custom_tag_in,
			se.custom_tag_out,
			se.custom_batch_no,
			se.custom_qty,
			se.custom_shift,
			# sed.gsm,
			# sed.meter,
			# sed.roll,
			# sed.colour,
			se.custom_wastage as wastage,
			sed.item_code,
			item.custom_feet as feet,
			sed.item_name,
			sed.qty,
			se.work_order,
			CASE
				WHEN EXISTS (
					SELECT 1
					FROM `tabStock Entry Type` setype
					WHERE setype.name = se.stock_entry_type
					AND setype.purpose = 'Manufacture'
				)
				THEN COALESCE(
					(
						SELECT woi.required_qty
						FROM `tabWork Order Item` woi
						WHERE woi.parent = se.work_order
						AND woi.item_code = sed.item_code
						LIMIT 1
					),
					sed.qty
				)
				ELSE NULL
			END AS work_order_qty,

			CASE
				WHEN EXISTS (
					SELECT 1
					FROM `tabStock Entry Type` setype
					WHERE setype.name = se.stock_entry_type
					AND setype.purpose = 'Manufacture'
				)
				THEN sed.qty - COALESCE(
					(
						SELECT woi.required_qty
						FROM `tabWork Order Item` woi
						WHERE woi.parent = se.work_order
						AND woi.item_code = sed.item_code
						LIMIT 1
					),
					sed.qty
				)
				ELSE NULL
			END AS variation,
			case
				when ifnull(sed.is_finished_item, 0) = 1 then ifnull(sed.t_warehouse, sed.s_warehouse)
				else ifnull(sed.s_warehouse, sed.t_warehouse)
			end as warehouse,
			case
				when ifnull(sed.is_scrap_item, 0) = 1 then 'Scrap'
				when ifnull(sed.is_finished_item, 0) = 1 then 'Finished'
				else 'Raw'
			end as item_type
		from `tabStock Entry` se
		inner join `tabStock Entry Detail` sed on sed.parent = se.name
		left join `tabItem` item on item.name = sed.item_code
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
	for row in rows:
		if row.get("work_order_qty"):
			row["variation_percentage"] = round(
				(row["variation"] / row["work_order_qty"]) * 100,
				2
			)
		else:
			row["variation_percentage"] = None

	last_stock_entry_id = None
	for row in rows:
		current_stock_entry_id = row.get("stock_entry_id")
		if current_stock_entry_id == last_stock_entry_id:
			row["posting_date"] = ""
			row["stock_entry_id"] = ""
			row["stock_entry_type"] = ""
			row["operator_name"] = ""
			row["machine_name"] = ""
			row["custom_tag_in"] = ""  
			row["custom_tag_out"] = ""
			row["custom_batch_no"] = ""
			row["custom_qty"] = ""
			row["custom_shift"] = ""
		else:
			last_stock_entry_id = current_stock_entry_id

	return rows
