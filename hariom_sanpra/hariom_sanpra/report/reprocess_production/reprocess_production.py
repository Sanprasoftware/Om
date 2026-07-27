# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	filters = frappe._dict(filters or {})
	columns = get_columns() 
	data = get_data(filters)

	return columns, data


def get_columns() -> list[dict]:
	
	return [
		{
			"label": _("Id"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Reprocess",
			"width": 150,
		},
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 120,
		},
		{
			"label": _("Shift"),
			"fieldname": "shift",
			"fieldtype": "Link",
			"options": "Shift",
			"width": 100,
		},
		{
			"label": _("Manpower"),
			"fieldname": "manpower",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Operator Name"),
			"fieldname": "operator_name",
			"fieldtype": "Multiselect",
			"width": 100,
		},
		{
			"label": _("Downtime"),
			"fieldname": "downtime",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Mesh Used"),
			"fieldname": "mesh_used",
			"fieldtype": "Data",
			"width": 100,
		},
  		{
			"label": _("Mesh Change"),
			"fieldname": "mesh_change",
			"fieldtype": "Int",
			"width": 100,
		},
		{
			"label": _("Reprocess Type"),
			"fieldname": "reprocess_type",
			"fieldtype": "Select",
			"width": 100,
		},
		{
			"label": _("M/C Name"),
			"fieldname": "mc_name",
			"fieldtype": "Link",
			"options": "Stock Entry Type",
			"width": 120,
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{
			"label": _("Mesh Use"),
			"fieldname": "mesh_use",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Qty Bags"),
			"fieldname": "qty_bags",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Target Warehouse"),
			"fieldname": "target_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		},
		{
			"label": _("UOM"),
			"fieldname": "uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 100,
		},
		{
			"label": _("Batch No"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 120,
		},
		# {
		# 	"label": _("M/c Start"),
		# 	"fieldname": "mc__start",
		# 	"fieldtype": "Data",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("M/c Stop"),
		# 	"fieldname": "mc_stop",
		# 	"fieldtype": "Data",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("Downtime Reason"),
		# 	"fieldname": "downtime_reason",
		# 	"fieldtype": "Data",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("Other Abnormality"),
		# 	"fieldname": "other_abrnormality",
		# 	"fieldtype": "Data",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("Stock Entry Type"),
		# 	"fieldname": "stock_entry_type",
		# 	"fieldtype": "Link",
		# 	"options": "Stock Entry Type",
		# 	"width": 100,
		# },
		# {
		# 	"label": _("Batch"),
		# 	"fieldname": "batch",
		# 	"fieldtype": "Link",
		# 	"options": "Batch No",
		# 	"width": 100,
		# },
  
		# --- Finished Item Child Table Fields ---
		# {
		# 	"label": _("Std Pkg"),
		# 	"fieldname": "std_pkg",
		# 	"fieldtype": "Data",
		# 	"width": 100,
		# },
  
	]


def get_data(filters) -> list[list]:
	data = []
	conditions = {"docstatus": 1}

	if filters.get("from_date"):
		conditions["date"] = [">=", filters.get("from_date")]

	if filters.get("to_date"):
		if "date" in conditions:
			conditions["date"] = [
				"between",
				[
					filters.get("from_date"),
					filters.get("to_date")
				]
			]
		else:
			conditions["date"] = ["<=", filters.get("to_date")]

	if filters.get("shift"):
		conditions["shift"] = filters.get("shift")
	
	if filters.get("reprocess_type"):
		conditions["reprocess_type"] = filters.get("reprocess_type")
	
	if filters.get("mc_name"):
		conditions["stock_entry_type"] = filters.get("mc_name")

	if filters.get("operator"):
		reprocess_names = frappe.get_all(
			"Operator Name Items",
			filters={
				"parenttype": "Reprocess",
				"parentfield": "operator_names",
				"operator_name": filters.get("operator"),
			},
			pluck="parent",
		)
		conditions["name"] = ["in", reprocess_names or [""]]

	all_data = frappe.get_all(
		"Reprocess",
		fields=[
			"name",
			"date",
			"shift",
			"manpower",
			# "mc__start",
			# "mc_stop",
			"downtime",
			# "downtime_reason",
			# "other_abrnormality",
			# "stock_entry_type",
			"mesh_used",
			"mesh_change",
			# "batch",
			"reprocess_type",
			"stock_entry_type",
		],
		filters=conditions
	)

	for row in all_data:
		operator_name = get_operator_names(row.name)
		# downtime_reason = get_downtime_reasons(row.name, row.downtime_reason)

		# Fetch child table items where is_finished_item = 1
		child_filters = {
			"parent": row.name,
			"is_finished_item": 1
		}

		if filters.get("item"):
			child_filters["item_code"] = filters.get("item")

		if filters.get("warehouse"):
			child_filters["target_warehouse"] = filters.get("warehouse")

		finished_items = frappe.get_all(
			"Reprocess Item",
			filters=child_filters,
			fields=[
				"item_code",
				"uom",
				"target_warehouse",
				"qty_bags",
				"mesh_use",
				# "std_pkg",
				"batch_no",
				"qty"
			]
		)

		# If no finished items, still show parent row with empty child fields
		if not finished_items:
			if (
					filters.get("item")
					or filters.get("warehouse")
			):
					continue
			data.append({
				"name": row.name,
				"date": row.date,
				"shift": row.shift,
				"manpower": row.manpower,
				"operator_name": operator_name,
				# "mc__start": row.mc__start,
				# "mc_stop": row.mc_stop,
				"downtime": row.downtime,
				# "downtime_reason": downtime_reason,
				# "other_abrnormality": row.other_abrnormality,
				# "stock_entry_type": row.stock_entry_type,
				"mesh_used": row.mesh_used,
				"mesh_change" : row.mesh_change,
				"mc_name": row.stock_entry_type,
				# "batch": row.batch,
				"item_code": None,
				"uom": None,
				"target_warehouse": None,
				"qty_bags": None,
				"mesh_use": None,
				# "std_pkg": None,
				"batch_no": None,
				"qty": None,
				"reprocess_type": row.reprocess_type,
			})
		else:
			# Create a row for each finished item
			# Parent fields shown only on first row, empty for subsequent rows
			for idx, item in enumerate(finished_items):
				if idx == 0:
					# First row: show all parent fields
					data.append({
						"name": row.name,
						"date": row.date,
						"shift": row.shift,
						"manpower": row.manpower,
						"operator_name": operator_name,
						# "mc__start": row.mc__start,
						# "mc_stop": row.mc_stop,
						"downtime": row.downtime,
						# "downtime_reason": downtime_reason,
						# "other_abrnormality": row.other_abrnormality,
						# "stock_entry_type": row.stock_entry_type,
						"mesh_used": row.mesh_used,
						"mesh_change" : row.mesh_change,
						"mc_name": row.stock_entry_type,
						# "batch": row.batch,
						"item_code": item.item_code,
						"uom": item.uom,
						"target_warehouse": item.target_warehouse,
						"qty_bags": item.qty_bags,
						"mesh_use": item.mesh_use,
						# "std_pkg": item.std_pkg,
						"batch_no": item.batch_no,
						"qty": item.qty,
						"reprocess_type": row.reprocess_type,
					})
				else:
					# Subsequent rows: parent fields empty, only item fields
					data.append({
						"name": None,
						"date": None,
						"shift": None,
						"manpower": None,
						"operator_name": None,
						# "mc__start": None,
						# "mc_stop": None,
						"downtime": None,
						# "downtime_reason": None,
						# "other_abrnormality": None,
						# "stock_entry_type": None,
						"mesh_used": None,
						"mesh_change":None,
						"mc_name": row.stock_entry_type,
						# "batch": None,
						"item_code": item.item_code,
						"uom": item.uom,
						"target_warehouse": item.target_warehouse,
						"qty_bags": item.qty_bags,
						"mesh_use": item.mesh_use,
						# "std_pkg": item.std_pkg,
						"batch_no": item.batch_no,
						"qty": item.qty,
						"reprocess_type": None,
					})

	return data


def get_operator_names(parent: str) -> str:
	operators = frappe.get_all(
		"Operator Name Items",
		filters={
			"parent": parent,
			"parenttype": "Reprocess",
			"parentfield": "operator_names",
		},
		fields=["operator_name"],
		order_by="idx",
	)

	operator_names = []
	for row in operators:
		operator = row.get("operator_name")
		if not operator:
			continue
		operator_names.append(
			frappe.db.get_value("Employee", operator, "employee_name") or operator
		)

	return ", ".join(operator_names)


# def get_downtime_reasons(parent: str, fallback: str | None = None) -> str | None:
# 	reasons = frappe.get_all(
# 		"Down Time Reason Items",
# 		filters={
# 			"parent": parent,
# 			"parenttype": "Reprocess",
# 			"parentfield": "downtime_reason",
# 		},
# 		fields=["down_time_reason"],
# 		order_by="idx",
# 	)

# 	formatted_reasons = [
# 		row.get("down_time_reason") for row in reasons if row.get("down_time_reason")
# 	]

# 	return ", ".join(formatted_reasons) or fallback
