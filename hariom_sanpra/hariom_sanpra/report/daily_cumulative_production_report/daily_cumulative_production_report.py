# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


PRODUCTION_FIELD_SPECS = [
	{"label": "Total Qty", "fieldname": "total_qty", "source": "custom_total_qty", "aggregate": "sum", "qty_field": True},
	{"label": "M/C Run", "fieldname": "mc_run", "source": "custom_mc_run", "aggregate": "sum"},
	{"label": "MTR", "fieldname": "mtr", "source": "custom_mtr", "aggregate": "sum"},
	{"label": "ACT.MTR", "fieldname": "act_mtr", "source": "custom_actmtr", "aggregate": "sum"},
	{"label": "Target MTR", "fieldname": "target_mtr", "source": "custom_target_mtr", "aggregate": "sum"},
	{"label": "D.Time", "fieldname": "d_time", "source": "custom_dtime", "aggregate": "sum"},
	{"label": "D.Time %", "fieldname": "d_time_percent", "source": "custom_dtime_", "aggregate": "calc"},
	{"label": "D.Time Reason", "fieldname": "d_time_reason", "source": "custom_d_time_reason", "aggregate": "text"},
	{"label": "Summary of D. Time", "fieldname": "summary_of_d_time", "source": "custom_summary_of_d_time", "aggregate": "text"},
	{"label": "Wastage", "fieldname": "wastage", "source": "custom_wastage", "aggregate": "sum"},
	{"label": "Weight Bridge Wastage", "fieldname": "weight_bridge_wastage", "source": "custom_weight_bridge_wastage", "aggregate": "sum"},
	{"label": "Wastage Difference", "fieldname": "wastage_difference", "source": "custom_wastage_difference", "aggregate": "sum"},
	{"label": "Total Wastage", "fieldname": "total_wastage", "source": "custom_total_wastage", "aggregate": "calc"},
	{"label": "LD", "fieldname": "ld", "source": "custom_ld", "aggregate": "sum"},
	{"label": "LD %", "fieldname": "ld_percent", "source": "custom_ld_", "aggregate": "calc"},
	{"label": "TRIM", "fieldname": "trim", "source": "custom_trim", "aggregate": "sum"},
	{"label": "TRIM %", "fieldname": "trim_percent", "source": "custom_trim_", "aggregate": "calc"},
	{"label": "Other", "fieldname": "other", "source": "custom_other", "aggregate": "sum"},
	{"label": "Other %", "fieldname": "other_percent", "source": "custom_other_", "aggregate": "calc"},
	{"label": "Size", "fieldname": "size", "source": "custom_size1", "aggregate": "text"},
	{"label": "STD GSM", "fieldname": "std_gsm", "source": "custom_std_gsm_", "aggregate": "average"},
	{"label": "ACT GSM", "fieldname": "act_gsm", "source": "custom_act_gsm", "aggregate": "calc"},
	# {"label": "Prod %", "fieldname": "prod_percent", "source": "custom_prod_", "aggregate": "calc"},
	# {"label": "Gain/Loss", "fieldname": "gain_loss", "source": "custom_gainloss", "aggregate": "average"},
	# {"label": "RPM A", "fieldname": "rpm_a", "source": "custom_rpm", "aggregate": "average"},
	# {"label": "RPM B", "fieldname": "rpm_b", "source": "custom_rpm_b", "aggregate": "average"},
	# {"label": "GRAM A", "fieldname": "gram_a", "source": "custom_gram", "aggregate": "average"},
	# {"label": "GRAM B", "fieldname": "gram_b", "source": "custom_gram_b", "aggregate": "average"},
	# {"label": "MPM", "fieldname": "mpm", "source": "custom_mpm", "aggregate": "average"},
	# {"label": "Flow % A", "fieldname": "flow_percent_a", "source": "custom_flow_", "aggregate": "average"},
	# {"label": "Flow % B", "fieldname": "flow_percent_b", "source": "custom_flow__b", "aggregate": "average"},
	# {"label": "GRAMAGE A", "fieldname": "gramage_a", "source": "custom_gramage", "aggregate": "average"},
	# {"label": "GRAMAGE B", "fieldname": "gramage_b", "source": "custom_gramage_b", "aggregate": "average"},
	# {"label": "GSM A", "fieldname": "gsm_a", "source": "custom_gsm1", "aggregate": "average"},
	# {"label": "GSM B", "fieldname": "gsm_b", "source": "custom_gsm_b", "aggregate": "average"},
	# {"label": "Total GSM", "fieldname": "total_gsm", "source": "custom_total_gsm", "aggregate": "average"},
	# {"label": "M/C Output A", "fieldname": "mc_output_a", "source": "custom_mc_output", "aggregate": "sum"},
	# {"label": "M/C Output B", "fieldname": "mc_output_b", "source": "custom_mc_output_b", "aggregate": "sum"},
]

NUMERIC_FIELDTYPES = {"Currency", "Float", "Int", "Percent"}


def execute(filters: dict | None = None):
	filters = frappe._dict(filters or {})
	report_fields = get_report_fields()
	return get_columns(filters, report_fields), get_data(filters, report_fields)


def get_report_fields() -> list[dict]:
	meta = frappe.get_meta("Stock Entry")
	fields = []

	for spec in PRODUCTION_FIELD_SPECS:
		meta_field = meta.get_field(spec["source"])
		if not meta_field and not frappe.db.has_column("Stock Entry", spec["source"]):
			continue

		field = spec.copy()
		field["label"] = meta_field.label if meta_field else spec["label"]
		field["fieldtype"] = meta_field.fieldtype if meta_field else "Float"
		fields.append(field)

	return fields


def get_columns(filters: frappe._dict, report_fields: list[dict]) -> list[dict]:
	columns = []

	if is_entry_wise(filters):
		columns.extend(
			[
				{
					"label": _("Date"),
					"fieldname": "date",
					"fieldtype": "Date",
					"width": 110,
				},
				{
					"label": _("Stock Entry"),
					"fieldname": "stock_entry",
					"fieldtype": "Link",
					"options": "Stock Entry",
					"width": 170,
				},
			]
		)

	columns.extend(
		[
			{
				"label": _("Item"),
				"fieldname": "item_code",
				"fieldtype": "Link",
				"options": "Item",
				"width": 150,
			},
			{
				"label": _("Item Name"),
				"fieldname": "item_name",
				"fieldtype": "Data",
				"width": 260,
			},
		]
	)

	for field in report_fields:
		column = {
			"label": _(field["label"]),
			"fieldname": field["fieldname"],
			"fieldtype": get_column_fieldtype(field),
			"width": get_column_width(field),
		}
		if column["fieldtype"] in NUMERIC_FIELDTYPES:
			column["precision"] = 2
		columns.append(column)

	return columns


def get_data(filters: frappe._dict, report_fields: list[dict]) -> list[dict]:
	conditions = ["se.docstatus in (0, 1)", "ifnull(sed.is_finished_item, 0) = 1"]
	sql_filters = {}

	if filters.get("from_date"):
		conditions.append("se.posting_date >= %(from_date)s")
		sql_filters["from_date"] = filters.from_date

	if filters.get("to_date"):
		conditions.append("se.posting_date <= %(to_date)s")
		sql_filters["to_date"] = filters.to_date

	if filters.get("item"):
		conditions.append("sed.item_code = %(item)s")
		sql_filters["item"] = filters.item

	if filters.get("manufacturing_type"):
		conditions.append("se.custom_manufacture_type = %(manufacturing_type)s")
		sql_filters["manufacturing_type"] = filters.manufacturing_type

	if is_entry_wise(filters):
		if filters.get("id"):
			conditions.append("se.name = %(id)s")
			sql_filters["id"] = filters.id

	doc_fields = ",\n\t\t\t".join(
		f"max(ifnull(se.{field['source']}, {get_sql_default(field)})) as {field['fieldname']}"
		for field in report_fields
		if not field.get("qty_field")
	)
	if doc_fields:
		doc_fields = f",\n\t\t\t{doc_fields}"

	rows = frappe.db.sql(
		f"""
		select
			se.name,
			sed.item_code,
			ifnull(sed.item_name, sed.item_code) as item_name,
			se.posting_date as date,
			sum(ifnull(sed.qty, 0)) as total_qty
			{doc_fields}
		from `tabStock Entry` se
		inner join `tabStock Entry Detail` sed on sed.parent = se.name
		where {" and ".join(conditions)}
		group by se.name, sed.item_code, sed.item_name, se.posting_date
		""",
		sql_filters,
		as_dict=True,
	)

	grouped = {}
	for row in rows:
		key = get_group_key(row, filters)
		if key not in grouped:
			grouped[key] = get_empty_group(row, report_fields, filters)

		item = grouped[key]
		if row.date:
			item["posting_dates"].add(row.date)

		for field in report_fields:
			fieldname = field["fieldname"]
			aggregate = field["aggregate"]

			if aggregate in ("sum", "calc"):
				item[fieldname] += flt(row.get(fieldname))
			elif aggregate == "average":
				value = flt(row.get(fieldname))
				if value:
					item["average_totals"][fieldname] += value
					item["average_counts"][fieldname] += 1
			elif aggregate == "text":
				add_text_value(item["text_values"][fieldname], row.get(fieldname))

	data = []
	for item in grouped.values():
		apply_calculations(item, report_fields)

		item.pop("posting_dates", None)
		item.pop("average_totals", None)
		item.pop("average_counts", None)
		item.pop("text_values", None)
		data.append(item)

	data = sorted(
		data,
		key=lambda row: (
			row.get("date") or "",
			row.get("stock_entry") or "",
			row.get("item_name") or "",
		),
	)

	if is_entry_wise(filters):
		hide_repeated_entry_values(data)

	return data


def get_empty_group(row: frappe._dict, report_fields: list[dict], filters: frappe._dict) -> dict:
	item = {
		"date": row.date,
		"item_code": row.item_code,
		"item_name": row.item_name,
		"posting_dates": set(),
		"average_totals": {},
		"average_counts": {},
		"text_values": {},
	}

	if is_entry_wise(filters):
		item["stock_entry"] = row.name

	for field in report_fields:
		fieldname = field["fieldname"]
		if field["aggregate"] == "average":
			item[fieldname] = 0
			item["average_totals"][fieldname] = 0
			item["average_counts"][fieldname] = 0
		elif field["aggregate"] == "text":
			item[fieldname] = ""
			item["text_values"][fieldname] = []
		else:
			item[fieldname] = 0

	return item


def apply_calculations(item: dict, report_fields: list[dict]) -> None:
	fieldnames = {field["fieldname"] for field in report_fields}
	production_days = len(item["posting_dates"]) or 1

	for field in report_fields:
		fieldname = field["fieldname"]
		if field["aggregate"] == "average":
			count = item["average_counts"][fieldname]
			item[fieldname] = item["average_totals"][fieldname] / count if count else 0
		elif field["aggregate"] == "text":
			item[fieldname] = ", ".join(item["text_values"][fieldname])

	if "target_mtr" in fieldnames and item.get("mc_run"):
		item["target_mtr"] = item["mc_run"] * 45

	if "prod_percent" in fieldnames:
		item["prod_percent"] = (
			(flt(item.get("act_mtr")) / flt(item.get("target_mtr"))) * 100
			if flt(item.get("target_mtr"))
			else 0
		)
	if "d_time_percent" in fieldnames:
		item["d_time_percent"] = (flt(item.get("d_time")) / (1440 * production_days)) * 100
	if "ld_percent" in fieldnames:
		item["ld_percent"] = (
			(flt(item.get("ld")) / flt(item.get("total_qty"))) * 100
			if flt(item.get("total_qty"))
			else 0
		)
	if "trim_percent" in fieldnames:
		item["trim_percent"] = (
			(flt(item.get("trim")) / flt(item.get("total_qty"))) * 100
			if flt(item.get("total_qty"))
			else 0
		)
	if "other_percent" in fieldnames:
		item["other_percent"] = (
			(flt(item.get("other")) / flt(item.get("total_qty"))) * 100
			if flt(item.get("total_qty"))
			else 0
		)
	if "total_wastage" in fieldnames:
		item["total_wastage"] = (
			flt(item.get("ld")) + flt(item.get("trim")) + flt(item.get("other"))
		)
	if "act_gsm" in fieldnames:
		item["act_gsm"] = (
			(flt(item.get("total_qty")) / flt(item.get("mtr"))) * 39.37 / 144 * 1000
			if flt(item.get("mtr"))
			else 0
		)


def get_group_key(row: frappe._dict, filters: frappe._dict) -> tuple:
	if is_entry_wise(filters):
		return row.date, row.name, row.item_code
	if is_date_range_item_wise(filters):
		return (row.item_code,)
	return row.date, row.item_code


def is_entry_wise(filters: frappe._dict) -> bool:
	return filters.get("report_based_on") == "Entry Wise"


def is_date_range_item_wise(filters: frappe._dict) -> bool:
	return bool(filters.get("from_date") and filters.get("to_date"))


def hide_repeated_entry_values(data: list[dict]) -> None:
	last_stock_entry = None
	for row in data:
		stock_entry = row.get("stock_entry")
		if stock_entry and stock_entry == last_stock_entry:
			row["date"] = None
			row["stock_entry"] = ""
		else:
			last_stock_entry = stock_entry


def add_text_value(values: list[str], value: str | None) -> None:
	value = (value or "").strip()
	if value and value not in values:
		values.append(value)


def get_column_fieldtype(field: dict) -> str:
	if field["aggregate"] == "text":
		return "Data"
	return field["fieldtype"] if field["fieldtype"] in NUMERIC_FIELDTYPES else "Float"


def get_column_width(field: dict) -> int:
	return 180 if field["aggregate"] == "text" else 120


def get_sql_default(field: dict) -> str:
	return "''" if field["aggregate"] == "text" else "0"
