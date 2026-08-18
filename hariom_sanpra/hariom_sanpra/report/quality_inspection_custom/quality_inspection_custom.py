# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns():

	return [

		# ---------------- Parent Fields ----------------

		{
			"label": _("ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Quality Inspection",
			"width": 180
		},
		{
			"label": _("Report Date"),
			"fieldname": "report_date",
			"fieldtype": "Date",
			"width": 120
		},
		{
			"label": _("Inspection Type"),
			"fieldname": "inspection_type",
			"fieldtype": "Data",
			"width": 130
		},
		{
			"label": _("Reference Type"),
			"fieldname": "reference_type",
			"fieldtype": "Data",
			"width": 140
		},
		{
			"label": _("Reference Name"),
			"fieldname": "reference_name",
			"fieldtype": "Dynamic Link",
			"options": "reference_type",
			"width": 180
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Template"),
			"fieldname": "quality_inspection_template",
			"fieldtype": "Link",
			"options": "Quality Inspection Template",
			"width": 220
		},
		{
			"label": _("Item Code"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 180
		},
		{
			"label": _("Item Name"),
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 250
		},
		{
			"label": _("Total Qty"),
			"fieldname": "total_qty",
			"fieldtype": "Float",
			"width": 100
		},

		# ---------------- Reading Fields ----------------

		{
			"label": _("Parameter"),
			"fieldname": "specification",
			"fieldtype": "Data",
			"width": 180
		},
		{
			"label": _("Parameter Group"),
			"fieldname": "parameter_group",
			"fieldtype": "Data",
			"width": 150
		},
		{
			"label": _("Reading Status"),
			"fieldname": "reading_status",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Numeric"),
			"fieldname": "numeric",
			"fieldtype": "Check",
			"width": 80
		},
		{
			"label": _("Reading Value"),
			"fieldname": "reading_value",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": _("Reading 1"),
			"fieldname": "reading_1",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 2"),
			"fieldname": "reading_2",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 3"),
			"fieldname": "reading_3",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 4"),
			"fieldname": "reading_4",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 5"),
			"fieldname": "reading_5",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 6"),
			"fieldname": "reading_6",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 7"),
			"fieldname": "reading_7",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 8"),
			"fieldname": "reading_8",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 9"),
			"fieldname": "reading_9",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading 10"),
			"fieldname": "reading_10",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Reading Avg"),
			"fieldname": "custom_reading_avg",
			"fieldtype": "Float",
			"precision": 2,
			"width": 100
		},
		{
			"label": _("Acceptance Criteria"),
			"fieldname": "value",
			"fieldtype": "Data",
			"width": 220
		},
		{
			"label": _("Manual Inspection"),
			"fieldname": "manual_inspection",
			"fieldtype": "Check",
			"width": 130
		},
		{
			"label": _("Minimum Value"),
			"fieldname": "min_value",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Maximum Value"),
			"fieldname": "max_value",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"label": _("Formula Based"),
			"fieldname": "formula_based_criteria",
			"fieldtype": "Check",
			"width": 120
		},
		{
			"label": _("Acceptance Formula"),
			"fieldname": "acceptance_formula",
			"fieldtype": "Data",
			"width": 200
		},

	]


def get_data(filters):

	conditions = ""

	if filters.get("from_date"):
		conditions += f" AND qi.report_date >= '{filters.get('from_date')}' "

	if filters.get("to_date"):
		conditions += f" AND qi.report_date <= '{filters.get('to_date')}' "

	if filters.get("inspection_type"):
		conditions += f" AND qi.inspection_type = '{filters.get('inspection_type')}' "

	if filters.get("reference_type"):
		conditions += f" AND qi.reference_type = '{filters.get('reference_type')}' "

	if filters.get("reference_name"):
		conditions += f" AND qi.reference_name = '{filters.get('reference_name')}' "

	if filters.get("status"):
		conditions += f" AND qi.status = '{filters.get('status')}' "

	if filters.get("quality_inspection_template"):
		conditions += f"""
			AND qi.quality_inspection_template =
			'{filters.get("quality_inspection_template")}'
		"""

	if filters.get("qi_id"):
		conditions += f" AND qi.name = '{filters.get('qi_id')}' "

	if filters.get("party_type") == "Supplier" and filters.get("party"):
		conditions += f"""
			AND qi.custom_supplier_name = '{filters.get("party")}'
		"""

	if filters.get("party_type") == "Customer" and filters.get("party"):
		conditions += f"""
			AND qi.custom_customer_name = '{filters.get("party")}'
		"""

	if filters.get("parameter"):
		conditions += f"""
			AND qir.specification = '{filters.get("parameter")}'
    """
	raw_data = frappe.db.sql(f"""

		SELECT

			qi.name,
			qi.report_date,
			qi.inspection_type,
			qi.reference_type,
			qi.reference_name,
			qi.status,
			qi.quality_inspection_template,
			qi.item_code,
			qi.item_name,
			qi.custom_total_qty as total_qty,	
   			qi.custom_supplier_name,
			qi.custom_customer_name,

			qir.specification,
			qir.parameter_group,
			qir.status as reading_status,
			qir.numeric,
			qir.reading_value,
			qir.reading_1,
			qir.reading_2,
			qir.reading_3,
			qir.reading_4,
			qir.reading_5,
			qir.reading_6,
			qir.reading_7,
			qir.reading_8,
			qir.reading_9,
			qir.reading_10,
            qir.custom_reading_avg,
			qir.value,
			qir.manual_inspection,
			qir.min_value,
			qir.max_value,
			qir.formula_based_criteria,
			qir.acceptance_formula

		FROM `tabQuality Inspection` qi

		LEFT JOIN `tabQuality Inspection Reading` qir
			ON qir.parent = qi.name

		WHERE qi.docstatus = 1
		{conditions}

		ORDER BY qi.report_date DESC, qi.name DESC, qir.idx ASC

	""", as_dict=1)

	data = []
	previous_qi = None

	for row in raw_data:

		# First row of each Quality Inspection
		if previous_qi != row.name:

			data.append({
				"name": row.name,
				"report_date": row.report_date,
				"inspection_type": row.inspection_type,
				"reference_type": row.reference_type,
				"reference_name": row.reference_name,
				"status": row.status,
				"quality_inspection_template": row.quality_inspection_template,
				"item_code": row.item_code,
				"total_qty": row.total_qty,
				"item_name": row.item_name,

				"specification": row.specification,
				"parameter_group": row.parameter_group,
				"reading_status": row.reading_status,
				"numeric": row.numeric,
				"reading_value": row.reading_value,
				"reading_1": row.reading_1,
				"reading_2": row.reading_2,
				"reading_3": row.reading_3,
				"reading_4": row.reading_4,
				"reading_5": row.reading_5,
				"reading_6": row.reading_6,
				"reading_7": row.reading_7,
				"reading_8": row.reading_8,
				"reading_9": row.reading_9,
				"reading_10": row.reading_10,
				"custom_reading_avg":row.custom_reading_avg,
				"value": row.value,
				"manual_inspection": row.manual_inspection,
				"min_value": row.min_value,
				"max_value": row.max_value,
				"formula_based_criteria": row.formula_based_criteria,
				"acceptance_formula": row.acceptance_formula
			})

			previous_qi = row.name

		# Child rows only
		else:

			data.append({
				"name": "",
				"report_date": "",
				"inspection_type": "",
				"reference_type": "",
				"reference_name": "",
				"status": "",
				"quality_inspection_template": "",
				"item_code": "",
				"item_name": "",
				"total_qty": row.total_qty,

				"specification": row.specification,
				"parameter_group": row.parameter_group,
				"reading_status": row.reading_status,
				"numeric": row.numeric,
				"reading_value": row.reading_value,
				"reading_1": row.reading_1,
				"reading_2": row.reading_2,
				"reading_3": row.reading_3,
				"reading_4": row.reading_4,
				"reading_5": row.reading_5,
				"reading_6": row.reading_6,
				"reading_7": row.reading_7,
				"reading_8": row.reading_8,
				"reading_9": row.reading_9,
				"reading_10": row.reading_10,
				"custom_reading_avg":row.custom_reading_avg,
				"value": row.value,
				"manual_inspection": row.manual_inspection,
				"min_value": row.min_value,
				"max_value": row.max_value,
				"formula_based_criteria": row.formula_based_criteria,
				"acceptance_formula": row.acceptance_formula
			})

	return data