# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns() -> list[dict]:
	return [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Data",
		},
		{
			"label": _("ID"),
			"fieldname": "id",
			"fieldtype": "Link",
			"options" : "Maintenance History Card"
		},
		{
			"label": _("Machine Name"),
			"fieldname": "machine_name",
			"fieldtype": "Link",
			"options" : "Machine Name"
		},
		{
			"label": _("Maintenance Person Name"),
			"fieldname": "maintenance_person_name",
			"fieldtype": "Data",
		},
		{
			"label": _("Details of Spare Items Used"),
			"fieldname": "details_of_spare_items_used",
			"fieldtype": "Link",
			"options" : "Item"
		},
		{
			"label": _("M/C On Time"),
			"fieldname": "mc_on_time",
			"fieldtype": "Time",
		},
		{
			"label": _("M/C Off Time"),
			"fieldname": "mc_off_time",
			"fieldtype": "Time",
		},
		{
			"label": _("Spare Item Cost"),
			"fieldname": "spare_item_cost",
			"fieldtype": "Float",
		},
		{
			"label": _("Nature Of Problem"),
			"fieldname": "nature_of_problem",
			"fieldtype": "Data",
		},
		{
			"label": _("Details of Maintenance Work Done"),
			"fieldname": "details_of_maintenance_work_done",
			"fieldtype": "Data",
		},
		{
			"label": _("Corrective Action Plan to Avoid"),
			"fieldname": "corrective_action_plan_to_avoid",
			"fieldtype": "Data",
		},
	]


def get_data(filters: frappe._dict) -> list[dict]:
    filter_dict = {}

    # ✅ Date range (both from & to)
    if filters.get("from_date") and filters.get("to_date"):
        filter_dict["date"] = ["between", [filters.from_date, filters.to_date]]

    # ✅ Only from_date
    elif filters.get("from_date"):
        filter_dict["date"] = [">=", filters.from_date]

    # ✅ Only to_date
    elif filters.get("to_date"):
        filter_dict["date"] = ["<=", filters.to_date]

    if filters.get("id"):
        filter_dict["name"] = filters.id

    if filters.get("machine_name"):
        filter_dict["machine_name"] = filters.machine_name

    data = frappe.get_all(
        "Maintenance History Card",
        fields=[
            "date",
            "name as id",
            "machine_name",
            "details_of_spare_items_used",
            "mc_on_time",
            "mc_off_time",
            "spare_item_cost",
            "nature_of_problem",
            "details_of_maintenance_work_done",
            "corrective_action_plan_to_avoid"
        ],
        filters=filter_dict
    )

    for row in data:
        doc = frappe.get_doc("Maintenance History Card", row.id)
        row["maintenance_person_name"] = get_operator_names(doc.get("maintenance_person_name") or [])

    return data


def get_operator_names(rows: list) -> str:
    operator_names = []

    for row in rows:
        operator_name = row.get("operator_name")
        if not operator_name:
            continue
        operator_names.append(
            frappe.db.get_value("Employee", operator_name, "employee_name") or operator_name
        )

    return ", ".join(operator_names)
