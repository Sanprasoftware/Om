# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters: dict | None = None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data  

def get_columns() -> list[dict]:
	return [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 110
		},
		{
			"label": _("Id"),
			"fieldname": "id",
			"fieldtype": "Link",
			"options": "Stock Entry",
			"width": 140
		},
		{
			"label": _("Job Name"),
			"fieldname": "job_name",
			"fieldtype": "Link",
			"options": "Item",
			"width": 300
		},
		{
			"label": _("OPTR Name"),
			"fieldname": "optr_name",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 100
		},
		{
			"label": _("M/C Name"),
			"fieldname": "mc_name",
			"fieldtype": "Link",
			"options": "Machine Name",
			"width": 160
		},
		{
			"label": _("Batch"),
			"fieldname": "batch",
			"fieldtype": "Link",
			"options": "Batch No",
			"width": 125
		},
		{
			"label": _("Shift"),
			"fieldname": "shift",
			"fieldtype": "Link",
			"options": "Shift",
			"width": 95
		},
		{
			"label": _("Man Power"),
			"fieldname": "man_power",
			"fieldtype": "Int",
			"width": 50
		},
		{
			"label": _("M/C Run"),
			"fieldname": "mc_run",
			"fieldtype": "Float",
			"width": 50,
			"precision":2
		},
		{
			"label": _("D.Time"),
			"fieldname": "d_time",
			"fieldtype": "Float",
			"width": 50,
			"precision":2
		},
		{
			"label": _("Target MTR"),
			"fieldname": "target_mtr",
			"fieldtype": "Float",
			"width": 50,
			"precision":2
		},
		{
			"label": _("ACT MTR"),
			"fieldname": "act_mtr",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Prod %"),
			"fieldname": "prod",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("MTR"),
			"fieldname": "mtr",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("NWT"),
			"fieldname": "nwt",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("LD"),
			"fieldname": "ld",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("LD %"),
			"fieldname": "ld_",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("TRIM"),
			"fieldname": "trim",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("TRIM %"),
			"fieldname": "trim_",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Other"),
			"fieldname": "other",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Other %"),
			"fieldname": "other_",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("STD GSM"),
			"fieldname": "std_gsm",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("ACT GSM"),
			"fieldname": "act_gsm",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Gain/Loss"),
			"fieldname": "gain_loss",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("RPM"),
			"fieldname": "rpm",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("MPM"),
			"fieldname": "mpm",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("GRAM"),
			"fieldname": "gram",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("GSM"),
			"fieldname": "gsm",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Flow %"),
			"fieldname": "flow",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Wastage"),
			"fieldname": "wastage",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Wastage Difference"),
			"fieldname": "wastage_difference",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Weight Bridge Wastage"),
			"fieldname": "weight_bridge_wastage",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("GRAMAGE"),
			"fieldname": "gramage",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},
		{
			"label": _("Current GSM"),
			"fieldname": "current_gsm",
			"fieldtype": "Float",
			"width": 75,
			"precision":2
		},

	]

def get_data(filters):
	data = []
	filters_dict = {"docstatus": ["in", [0, 1]]}

	# ✅ Date filter fix
	if filters.get("from_date") and filters.get("to_date"):
		filters_dict["posting_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]

	elif filters.get("from_date"):
		filters_dict["posting_date"] = [">=", filters.get("from_date")]

	elif filters.get("to_date"):
		filters_dict["posting_date"] = ["<=", filters.get("to_date")]

	if filters.get("id"):
		filters_dict["name"] = filters.get("id")

	if filters.get("operator_name"):
		filters_dict["custom_operator_name"] = filters.get("operator_name")

	if filters.get("mc_name"):
		filters_dict["custom_machine_name"] = filters.get("mc_name")

	if filters.get("custom_shift"):
		filters_dict["custom_shift"] = filters.get("custom_shift")

	if filters.get("batch_no"):
		filters_dict["custom_batch_no"] = filters.get("batch_no")

	stock_entries = frappe.get_all(
		"Stock Entry",
		filters=filters_dict,
		fields=["name"]
	)
	
	for se in stock_entries:
		doc = frappe.get_doc("Stock Entry", se.name)
		employee_name = frappe.db.get_value("Employee",doc.custom_operator_name,"employee_name")
		for item in doc.items:
			# frappe.msgprint(str(item))
			if item.is_finished_item:
				data.append({
					"date" : doc.posting_date,
					"id": doc.name,
					"job_name": item.item_code,
					"optr_name": employee_name,
					"mc_name" : doc.custom_machine_name,
					"batch" : doc.custom_batch_no,
					"shift" : doc.custom_shift,
					"man_power" : doc.custom_manpower,
					"mc_run" : doc.custom_mc_run,
					"d_time" : doc.custom_dtime,
					"target_mtr" : doc.custom_target_mtr,
					"act_mtr" : doc.custom_actmtr,
					"prod" : doc.custom_prod_,
					"mtr" : doc.custom_mtr,
					"nwt" : item.qty,
					"ld" : doc.custom_ld,
					"ld_" : doc.custom_ld_,
					"trim" : doc.custom_trim,
					"trim_" : doc.custom_trim_,
					"other" : doc.custom_other,
					"other_" : doc.custom_other_,
					"std_gsm" : doc.custom_std_gsm_,
					"act_gsm" : doc.custom_act_gsm,
					"gain_loss" : doc.custom_gainloss,
					"rpm" : doc.custom_rpm,
					"mpm" : doc.custom_mpm,
					"gram" : doc.custom_gram,
					"gsm" : doc.custom_gsm1,
					"flow" : doc.custom_flow_,
					"wastage" : doc.custom_wastage,
					"wastage_difference": doc.custom_wastage_difference,
					"weight_bridge_wastage": doc.custom_weight_bridge_wastage,
					"gramage":doc.custom_gramage,
					"current_gsm":doc.custom_current_gsm



				})
	return data