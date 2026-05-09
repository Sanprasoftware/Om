# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _

DOCTYPE = "Maintenance"
EXCLUDED_FIELDS = {"naming_series", "amended_from"}
NON_DATA_FIELD_TYPES = {
	"Section Break",
	"Column Break",
	"Tab Break",
	"Fold",
	"Heading",
	"HTML",
	"Button",
}


def execute(filters: dict | None = None):
	filters = filters or {}
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns() -> list[dict]:
	meta = frappe.get_meta(DOCTYPE)
	columns = [
		{
			"label": _("ID"),
			"fieldname": "name",
			"fieldtype": "Link",
			"options": DOCTYPE,
			"width": 180,
		}
	]

	for df in meta.fields:
		if df.fieldtype in NON_DATA_FIELD_TYPES or not df.fieldname or df.fieldname in EXCLUDED_FIELDS:
			continue

		if df.fieldtype == "Table":
			columns.append(
				{
					"label": _(df.label or frappe.unscrub(df.fieldname)),
					"fieldname": f"{df.fieldname}_summary",
					"fieldtype": "Data",
					"width": 260,
				}
			)
			continue

		if df.fieldtype == "Table MultiSelect":
			columns.append(
				{
					"label": _(df.label or frappe.unscrub(df.fieldname)),
					"fieldname": df.fieldname,
					"fieldtype": "Data",
					"width": 220,
				}
			)
			continue

		columns.append(
			{
				"label": _(df.label or frappe.unscrub(df.fieldname)),
				"fieldname": df.fieldname,
				"fieldtype": df.fieldtype or "Data",
				"options": df.options,
				"width": get_column_width(df.fieldtype),
			}
		)

	return columns


def get_data(filters: dict) -> list[dict]:
	meta = frappe.get_meta(DOCTYPE)
	direct_fields = ["name"]
	table_fields = []
	table_multiselect_fields = []

	for df in meta.fields:
		if df.fieldtype in NON_DATA_FIELD_TYPES or not df.fieldname or df.fieldname in EXCLUDED_FIELDS:
			continue

		if df.fieldtype == "Table":
			table_fields.append(df)
			continue

		if df.fieldtype == "Table MultiSelect":
			table_multiselect_fields.append(df)
			continue

		direct_fields.append(df.fieldname)

	data = frappe.get_all(
		DOCTYPE,
		filters=get_conditions(filters),
		fields=direct_fields,
		order_by="issue_date desc, creation desc",
	)

	if not (table_fields or table_multiselect_fields) or not data:
		return data

	for row in data:
		doc = frappe.get_doc(DOCTYPE, row["name"])
		for df in table_fields:
			row[f"{df.fieldname}_summary"] = format_child_table(doc.get(df.fieldname) or [])
		for df in table_multiselect_fields:
			row[df.fieldname] = format_operator_names(doc.get(df.fieldname) or [])

	return data


def get_conditions(filters: dict) -> dict:
	conditions = {}

	if filters.get("id"):
		conditions["name"] = filters["id"]

	if filters.get("from_date"):
		conditions["issue_date"] = [">=", filters["from_date"]]

	if filters.get("to_date"):
		if conditions.get("issue_date"):
			conditions["issue_date"] = ["between", [filters["from_date"], filters["to_date"]]]
		else:
			conditions["issue_date"] = ["<=", filters["to_date"]]

	if filters.get("maintains_oper"):
		conditions["maintains_oper"] = filters["maintains_oper"]

	if filters.get("machine_name"):
		conditions["machine_name"] = filters["machine_name"]

	if filters.get("operator_name"):
		maintenance_names = frappe.get_all(
			"Operator Name Items",
			filters={
				"parenttype": DOCTYPE,
				"parentfield": "operator_name",
				"operator_name": filters["operator_name"],
			},
			pluck="parent",
		)
		if filters.get("id"):
			if filters["id"] not in maintenance_names:
				conditions["name"] = ["in", [""]]
		else:
			conditions["name"] = ["in", maintenance_names or [""]]

	return conditions


def format_operator_names(rows: list) -> str:
	operator_names = []

	for row in rows:
		operator_name = row.get("operator_name")
		if not operator_name:
			continue
		operator_names.append(
			frappe.db.get_value("Employee", operator_name, "employee_name") or operator_name
		)

	return ", ".join(operator_names)


def format_child_table(rows: list) -> str:
	formatted_rows = []

	for row in rows:
		values = []
		for key, value in row.as_dict().items():
			if key in {"name", "owner", "creation", "modified", "modified_by", "parent", "parentfield", "parenttype", "docstatus", "idx", "doctype"}:
				continue
			if value in (None, "", []):
				continue
			values.append(f"{frappe.unscrub(key)}: {value}")

		if values:
			formatted_rows.append(", ".join(values))

	return " | ".join(formatted_rows)


def get_column_width(fieldtype: str | None) -> int:
	if fieldtype in {"Check", "Int", "Float", "Currency", "Percent"}:
		return 100
	if fieldtype in {"Date"}:
		return 110
	if fieldtype in {"Datetime"}:
		return 150
	if fieldtype in {"Small Text", "Text", "Long Text", "Text Editor"}:
		return 220
	if fieldtype in {"Link", "Dynamic Link", "Select"}:
		return 160
	return 140
