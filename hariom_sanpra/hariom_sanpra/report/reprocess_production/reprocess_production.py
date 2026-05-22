# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	columns = get_columns() 
	data = get_data()

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
			"label": _("M/c Start"),
			"fieldname": "mc__start",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("M/c Stop"),
			"fieldname": "mc_stop",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Downtime"),
			"fieldname": "downtime",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Downtime Reason"),
			"fieldname": "downtime_reason",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Other Abnormality"),
			"fieldname": "other_abrnormality",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Stock Entry Type"),
			"fieldname": "stock_entry_type",
			"fieldtype": "Link",
			"options": "Stock Entry Type",
			"width": 100,
		},
		{
			"label": _("Mesh Used"),
			"fieldname": "mesh_used",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Batch"),
			"fieldname": "batch",
			"fieldtype": "Link",
			"options": "Batch No",
			"width": 100,
		},
		# --- Finished Item Child Table Fields ---
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
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
			"label": _("Target Warehouse"),
			"fieldname": "target_warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 150,
		},
		{
			"label": _("Qty Bags"),
			"fieldname": "qty_bags",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Mesh Use"),
			"fieldname": "mesh_use",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Std Pkg"),
			"fieldname": "std_pkg",
			"fieldtype": "Data",
			"width": 100,
		},
		{
			"label": _("Batch No"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 120,
		},
		{
			"label": _("Qty"),
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 100,
		},
	]


def get_data() -> list[list]:
	data = []

	all_data = frappe.get_all("Reprocess", ["name", "date", "shift", "manpower", "operator_name", "mc__start", "mc_stop", "downtime", "downtime_reason", "other_abrnormality", "stock_entry_type", "mesh_used", "batch"])

	for row in all_data:
		# Fetch child table items where is_finished_item = 1
		finished_items = frappe.get_all(
			"Reprocess Item",  # Replace with your actual child table DocType name
			filters={
				"parent": row.name,
				"is_finished_item": 1
			},
			fields=["item_code", "uom", "target_warehouse", "qty_bags", "mesh_use", "std_pkg", "batch_no", "qty"]
		)

		# If no finished items, still show parent row with empty child fields
		if not finished_items:
			data.append({
				"name": row.name,
				"date": row.date,
				"shift": row.shift,
				"manpower": row.manpower,
				"operator_name": row.operator_name,
				"mc__start": row.mc__start,
				"mc_stop": row.mc_stop,
				"downtime": row.downtime,
				"downtime_reason": row.downtime_reason,
				"other_abrnormality": row.other_abrnormality,
				"stock_entry_type": row.stock_entry_type,
				"mesh_used": row.mesh_used,
				"batch": row.batch,
				"item_code": None,
				"uom": None,
				"target_warehouse": None,
				"qty_bags": None,
				"mesh_use": None,
				"std_pkg": None,
				"batch_no": None,
				"qty": None,
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
						"operator_name": row.operator_name,
						"mc__start": row.mc__start,
						"mc_stop": row.mc_stop,
						"downtime": row.downtime,
						"downtime_reason": row.downtime_reason,
						"other_abrnormality": row.other_abrnormality,
						"stock_entry_type": row.stock_entry_type,
						"mesh_used": row.mesh_used,
						"batch": row.batch,
						"item_code": item.item_code,
						"uom": item.uom,
						"target_warehouse": item.target_warehouse,
						"qty_bags": item.qty_bags,
						"mesh_use": item.mesh_use,
						"std_pkg": item.std_pkg,
						"batch_no": item.batch_no,
						"qty": item.qty,
					})
				else:
					# Subsequent rows: parent fields empty, only item fields
					data.append({
						"name": None,
						"date": None,
						"shift": None,
						"manpower": None,
						"operator_name": None,
						"mc__start": None,
						"mc_stop": None,
						"downtime": None,
						"downtime_reason": None,
						"other_abrnormality": None,
						"stock_entry_type": None,
						"mesh_used": None,
						"batch": None,
						"item_code": item.item_code,
						"uom": item.uom,
						"target_warehouse": item.target_warehouse,
						"qty_bags": item.qty_bags,
						"mesh_use": item.mesh_use,
						"std_pkg": item.std_pkg,
						"batch_no": item.batch_no,
						"qty": item.qty,
					})

	return data