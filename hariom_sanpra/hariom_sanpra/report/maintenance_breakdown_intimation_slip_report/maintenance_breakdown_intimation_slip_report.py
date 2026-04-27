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
			"options" : "Maintenance Breakdown Intimation Slip"
		},
		{
			"label": _("Machine Name"),
			"fieldname": "machine_name",
			"fieldtype": "Link",
			"options" : "Machine Name"
		},
		{
			"label": _("Time"),
			"fieldname": "time",
			"fieldtype": "Time",
		},
		{
			"label": _("Shift"),
			"fieldname": "shift",
			"fieldtype": "Link",
			"options": "Shift"
		},
        {
			"label": _("Dept. Name "),
			"fieldname": "dep_name",
			"fieldtype": "Link",
			"options": "Department"
		},
        {
			"label": _("M/c Return to Production"),
			"fieldname": "mc_return_to_prod",
			"fieldtype": "Datetime",
		},
        {
			"label": _("Employee Name"),
			"fieldname": "emp_name",
			"fieldtype": "Link",
			"options" : "Employee Name"
		},
        {
			"label": _("Machine Code"),
			"fieldname": "machine_code",
			"fieldtype": "Data",
			"options" : "Machine Code"
		},
        {
			"label": _("Total Down Time"),
			"fieldname": "total_down_time",
			"fieldtype": "Float",
		},
        {
			"label": _("Received By"),
			"fieldname": "received_by",
			"fieldtype": "Link",
			"options" : "Received By"
		},
        {
			"label": _("Attended By"),
			"fieldname": "attended_by",
			"fieldtype": "Link",
			"options" : "Attended By"
		},
        {
			"label": _("Details of Repair work"),
			"fieldname": "details_of_repair_work",
			"fieldtype": "Small Text",
		},
        {
			"label": _("Maintenance I/C"),
			"fieldname": "maintenance_ic",
			"fieldtype": "Link",
			"options" : "Employee"
		},
        {
			"label": _("Production Dept"),
			"fieldname": "production_dept",
			"fieldtype": "Link",
			"options" : "Employee"
		},


	]


def get_data(filters: frappe._dict) -> list[dict]:
    filter_dict = {}

    if filters.get("from_date") and filters.get("to_date"):
        filter_dict["date"] = ["between", [filters.from_date, filters.to_date]]

    elif filters.get("from_date"):
        filter_dict["date"] = [">=", filters.from_date]

    elif filters.get("to_date"):
        filter_dict["date"] = ["<=", filters.to_date]

    if filters.get("id"):
        filter_dict["name"] = filters.id

    if filters.get("machine_name"):
        filter_dict["machine_name"] = filters.machine_name

    data = frappe.get_all(
        "Maintenance Breakdown Intimation Slip",
        fields=[
            "date",
            "name as id",
            "machine_name",
            "time",
            "shift",
            "dep_name",
            "mc_return_to_prod",
            "emp_name",
            "machine_code",
            "total_down_time",
            "received_by",
            "attended_by",
            "details_of_repair_work",
            "maintenance_ic",
            "production_dept"
        ],
        filters=filter_dict
    )
    for row in data:
        if row.get("emp_name"):
            row["emp_name"] = frappe.db.get_value("Employee", row["emp_name"], "employee_name")

        if row.get("received_by"):
            row["received_by"] = frappe.db.get_value("Employee", row["received_by"], "employee_name")

        if row.get("attended_by"):
            row["attended_by"] = frappe.db.get_value("Employee", row["attended_by"], "employee_name")

    return data