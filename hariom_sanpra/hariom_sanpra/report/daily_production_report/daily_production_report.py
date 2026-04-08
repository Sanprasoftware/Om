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
			"label": _("Job Name"),
			"fieldname": "job_name",
			"fieldtype": "Link",
			"options": "Item",
			"width": 200
		},
		{
			"label": _("M/C Run"),
			"fieldname": "mc_run",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("D.Time"),
			"fieldname": "d_time",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Target MTR"),
			"fieldname": "target_mtr",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("ACT MTR"),
			"fieldname": "act_mtr",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Prod %"),
			"fieldname": "prod",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Wastage"),
			"fieldname": "wastage",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("MTR"),
			"fieldname": "mtr",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("NWT"),
			"fieldname": "nwt",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("LD"),
			"fieldname": "ld",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("LD %"),
			"fieldname": "ld_",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("TRIM"),
			"fieldname": "trim",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("TRIM %"),
			"fieldname": "trim_",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Other"),
			"fieldname": "other",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Other %"),
			"fieldname": "other_",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("STD GSM"),
			"fieldname": "std_gsm",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("ACT GSM"),
			"fieldname": "act_gsm",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Gain/Loss"),
			"fieldname": "gain_loss",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("RPM"),
			"fieldname": "rpm",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("MPM"),
			"fieldname": "mpm",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("GRAM"),
			"fieldname": "gram",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("GSM"),
			"fieldname": "gsm",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Flow %"),
			"fieldname": "flow",
			"fieldtype": "Data",
			"width": 150
		},
	]

def get_data():
	data = []
	stock_entries = frappe.get_all("Stock Entry",filters={"docstatus": 0},fields=["name"])
	for se in stock_entries:
		doc = frappe.get_doc("Stock Entry", se.name)
		for item in doc.items:
			# frappe.msgprint(str(item))
			if item.is_finished_item:
				data.append({
					"job_name": item.item_code,
					"mc_run" : doc.custom_mc_run,
					"d_time" : doc.custom_dtime,
					"target_mtr" : doc.custom_target_mtr,
					"act_mtr" : doc.custom_actmtr,
					"prod" : doc.custom_prod_,
					"wastage" : doc.custom_wastage,
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
				})
	return data