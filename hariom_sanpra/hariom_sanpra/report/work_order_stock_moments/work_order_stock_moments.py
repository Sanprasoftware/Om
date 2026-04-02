# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_data(report_filters):
	conditions = [
		"wo.docstatus = 1",
		"wo.status in ('In Process', 'Completed', 'Stopped')",
		"wo.creation between %(from_date)s and %(to_date)s",
	]

	for field, condition in {
		"company": "wo.company = %(company)s",
		"name": "wo.name = %(name)s",
		"job_card": "jc.name = %(job_card)s",
		"production_item": "wo.production_item = %(production_item)s",
		"status": "wo.status = %(status)s",
	}.items():
		if report_filters.get(field):
			conditions.append(condition)

	rows = frappe.db.sql(
		f"""
		select
			wo.name as name,
			wo.status as status,
			jc.name as job_card,
			jc.operation,
			wo.production_item,
			wo.qty,
			wo.produced_qty,
			jci.item_code as raw_material_item_code,
			jci.item_name as raw_material_name,
			coalesce(jci.required_qty, 0) as required_qty,
			coalesce(jci.transferred_qty, 0) as transferred_qty,
			coalesce(jci.consumed_qty, 0) as consumed_qty,
			coalesce(ret.returned_qty, 0) as returned_qty
		from `tabWork Order` wo
		inner join `tabJob Card` jc on jc.work_order = wo.name
		inner join `tabJob Card Item` jci on jci.parent = jc.name
		left join (
			select
				se.job_card,
				sed.item_code,
				sum(abs(sed.qty)) as returned_qty
			from `tabStock Entry` se
			inner join `tabStock Entry Detail` sed on sed.parent = se.name
			where
				se.docstatus = 1
				and sed.docstatus = 1
				and se.is_return = 1
			group by se.job_card, sed.item_code
		) ret on ret.job_card = jc.name and ret.item_code = jci.item_code
		where {' and '.join(conditions)}
		order by wo.name, jc.name, jci.item_code
		""",
		report_filters,
		as_dict=True,
	)

	data = []
	jc_items = {}

	for d in rows:
		d.extra_consumed_qty = 0.0
		if d.consumed_qty and d.consumed_qty > d.required_qty:
			d.extra_consumed_qty = d.consumed_qty - d.required_qty

		if d.extra_consumed_qty or not report_filters.get("show_extra_consumed_materials"):
			jc_items.setdefault((d.name, d.job_card), []).append(d)

	for _key, jc_data in jc_items.items():
		for index, row in enumerate(jc_data):
			if index != 0:
				# Show parent details only once for each Work Order + Job Card block.
				for field in ["name", "status", "job_card", "operation", "production_item", "qty", "produced_qty"]:
					row[field] = ""

			data.append(row)

	return data


def get_columns():
	return [
		{
			"label": _("Work Order"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Work Order",
			"width": 120,
		},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{
			"label": _("Job Card"),
			"fieldname": "job_card",
			"fieldtype": "Link",
			"options": "Job Card",
			"width": 130,
		},
		{
			"label": _("Operation"),
			"fieldname": "operation",
			"fieldtype": "Link",
			"options": "Operation",
			"width": 140,
		},
		{
			"label": _("Production Item"),
			"fieldname": "production_item",
			"fieldtype": "Link",
			"options": "Item",
			"width": 130,
		},
		{"label": _("Qty to Produce"), "fieldname": "qty", "fieldtype": "Float", "width": 120},
		{"label": _("Produced Qty"), "fieldname": "produced_qty", "fieldtype": "Float", "width": 110},
		{
			"label": _("Raw Material Item"),
			"fieldname": "raw_material_item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150,
		},
		{"label": _("Item Name"), "fieldname": "raw_material_name", "width": 130},
		{"label": _("Required Qty"), "fieldname": "required_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Transferred Qty"),
			"fieldname": "transferred_qty",
			"fieldtype": "Float",
			"width": 100,
		},
		{"label": _("Consumed Qty"), "fieldname": "consumed_qty", "fieldtype": "Float", "width": 100},
		{
			"label": _("Extra Consumed Qty"),
			"fieldname": "extra_consumed_qty",
			"fieldtype": "Float",
			"width": 120,
		},
		{
			"label": _("Returned Qty"),
			"fieldname": "returned_qty",
			"fieldtype": "Float",
			"width": 100,
		},
	]
