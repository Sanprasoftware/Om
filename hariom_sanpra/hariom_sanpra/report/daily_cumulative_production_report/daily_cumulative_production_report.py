# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import flt


PRODUCTION_FIELD_SPECS = [
	# {"label": _("Purpose"),"fieldname": "purpose","fieldtype": "Data","source": "purpose", "aggregate": "text",},
	# {"label": _("manufacturing type"),"fieldname": "manufacture_type","source": "custom_manufacture_type","aggregate": "text",},
	{"label": "Total Qty", "fieldname": "total_qty", "source": "custom_total_qty", "aggregate": "sum", "qty_field": True},
	{"label": "M/C Run", "fieldname": "mc_run", "source": "custom_mc_run", "aggregate": "sum"},
	{"label": "MTR", "fieldname": "mtr", "source": "custom_mtr", "aggregate": "sum" , "hidden": 1},
	{"label": "ACT.MTR", "fieldname": "act_mtr", "source": "custom_actmtr", "aggregate": "sum"},
	{"label": "Target MTR", "fieldname": "target_mtr", "source": "custom_target_mtr", "aggregate": "sum"},
	{"label": "Prod %", "fieldname": "prod_percent", "source": "custom_prod_", "aggregate": "calc"},
	{"label": "D.Time", "fieldname": "d_time", "source": "custom_dtime", "aggregate": "sum"},
	{"label": "D.Time %", "fieldname": "d_time_percent", "source": "custom_dtime_", "aggregate": "calc"},
	{"label": "D.Time Reason", "fieldname": "d_time_reason", "source": "custom_d_time_reason", "aggregate": "text"},
	{"label": "Summary of D. Time", "fieldname": "summary_of_d_time", "source": "custom_summary_of_d_time", "aggregate": "text"},
	{"label": "Wastage", "fieldname": "wastage", "source": "custom_wastage", "aggregate": "sum"},
	{"label": "Weight Bridge Wastage", "fieldname": "weight_bridge_wastage", "source": "custom_weight_bridge_wastage", "aggregate": "sum"},
	{"label": "Wastage Difference", "fieldname": "wastage_difference", "source": "custom_wastage_difference", "aggregate": "sum"},
	{"label": "Wastage %", "fieldname": "wastage_percent", "source": "custom_total_wastage", "aggregate": "sum"},
	{"label": "LD", "fieldname": "ld", "source": "custom_ld", "aggregate": "sum"},
	{"label": "LD %", "fieldname": "ld_percent", "source": "custom_ld_", "aggregate": "calc"},
	{"label": "TRIM", "fieldname": "trim", "source": "custom_trim", "aggregate": "sum"},
	{"label": "TRIM %", "fieldname": "trim_percent", "source": "custom_trim_", "aggregate": "calc"},
	{"label": "Other", "fieldname": "other", "source": "custom_other", "aggregate": "sum"},
	{"label": "Other %", "fieldname": "other_percent", "source": "custom_other_", "aggregate": "calc"},
	{"label": "Size", "fieldname": "size", "source": "custom_size1", "aggregate": "text"},
	{"label": "STD GSM", "fieldname": "std_gsm", "source": "custom_std_gsm_", "aggregate": "average"},
	{"label": "ACT GSM", "fieldname": "act_gsm", "source": "custom_act_gsm", "aggregate": "calc"},
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

TOTAL_SUM_FIELDS = {
	"total_qty",
	"act_mtr",
	"target_mtr",
	"d_time",
	"wastage",
	"weight_bridge_wastage",
	"wastage_difference",
	"ld",
	"trim",
	"other",
	"size",
	"mc_run",
}

TOTAL_AVERAGE_FIELDS = {
	"prod_percent",
	"d_time_percent",
	"wastage_percent",
	"ld_percent",
	"trim_percent",
	"other_percent",
	"std_gsm",
	"act_gsm",
}


def execute(filters: dict | None = None):
	filters = frappe._dict(filters or {})
	report_fields = get_report_fields()
	columns = get_columns(filters, report_fields)
	data = get_data(filters, report_fields)
	add_combined_total_row(data, filters)
	return columns, data, None, None, None, True


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
		if meta_field and meta_field.fieldtype == "Table MultiSelect":
			field["child_table"] = meta_field.options
			field["child_value_field"] = get_table_multiselect_value_field(meta_field.options)
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
			{
				"label": _("Machine Name"),
				"fieldname": "machine_name",
				"fieldtype": "Link",
				"options": "Machine Name",
				"width": 160,
			},
			{
				"label": _("Warehouse"),
				"fieldname": "warehouse",
				"fieldtype": "Link",
				"options": "Warehouse",
				"width": 180,
			},
		]
	)

	for field in report_fields:
		if field.get("hidden"):
			continue
		column = {
			"label": _(field["label"]),
			"fieldname": field["fieldname"],
			"fieldtype": get_column_fieldtype(field),
			"width": get_column_width(field),
		}
		if column["fieldtype"] in NUMERIC_FIELDTYPES:
			column["precision"] = 6 if field["fieldname"] == "wastage_percent" else 2
		columns.append(column)

	return columns


def get_data(filters: frappe._dict, report_fields: list[dict]) -> list[dict]:
	conditions = [
		"se.docstatus = 1",
		"ifnull(sed.is_finished_item, 0) = 1",
		"se.purpose = 'Manufacture'",

	]
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

	if filters.get("machine_name"):
		conditions.append("se.custom_machine_name = %(machine_name)s")
		sql_filters["machine_name"] = filters.machine_name

	warehouse_expression = get_warehouse_expression()
	if filters.get("warehouse"):
		conditions.append(f"{warehouse_expression} = %(warehouse)s")
		sql_filters["warehouse"] = filters.warehouse

	if is_entry_wise(filters):
		if filters.get("id"):
			conditions.append("se.name = %(id)s")
			sql_filters["id"] = filters.id

	# doc_fields = ",\n\t\t\t".join(
	# 	f"max(ifnull(se.{field['source']}, {get_sql_default(field)})) as {field['fieldname']}"
	# 	for field in report_fields
	# 	if not field.get("qty_field")
	# )

	doc_fields = ",\n\t\t\t".join(
		get_doc_field_sql(field)
		for field in report_fields
		if not field.get("qty_field")
	)
	if doc_fields:
		doc_fields = f",\n\t\t\t{doc_fields}"

	table_multiselect_joins = "\n\t\t".join(
		get_table_multiselect_join(field)
		for field in report_fields
		if field.get("child_table") and field.get("child_value_field")
	)

	entry_wise = is_entry_wise(filters)
	select_detail_fields = ",\n\t\t\tsed.name as detail_name,\n\t\t\tsed.idx as detail_idx" if entry_wise else ""
	group_by_fields = (
		f"se.name, sed.name, sed.item_code, sed.item_name, se.posting_date, sed.idx, se.custom_machine_name, {warehouse_expression}"
		if entry_wise
		else f"se.name, sed.item_code, sed.item_name, se.posting_date, se.custom_machine_name, {warehouse_expression}"
	)

	rows = frappe.db.sql(
		f"""
		select
			se.name{select_detail_fields},
			sed.item_code,
			ifnull(sed.item_name, sed.item_code) as item_name,
			se.custom_machine_name as machine_name,
			{warehouse_expression} as warehouse,
			se.purpose as purpose,
			se.custom_manufacture_type as manufacture_type,

			se.posting_date as date,
			sum(ifnull(sed.qty, 0)) as total_qty
			{doc_fields}
		from `tabStock Entry` se
		inner join `tabStock Entry Detail` sed on sed.parent = se.name
		{table_multiselect_joins}
		where {" and ".join(conditions)}
		group by {group_by_fields}
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

			if fieldname == "size":
				item["size_values"].extend(get_numeric_values(row.get(fieldname)))

			if fieldname in TOTAL_AVERAGE_FIELDS:
				item["total_average_totals"][fieldname] += flt(row.get(fieldname))
				item["total_average_counts"][fieldname] += 1

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

		if not is_entry_wise(filters):
			for fieldname in TOTAL_AVERAGE_FIELDS:
				# STD GSM is already averaged by apply_calculations() across the
				# filtered item's Stock Entries. Do not replace it with the sum.
				if fieldname in ("prod_percent", "std_gsm", "act_gsm"):
					continue
				if item["total_average_counts"].get(fieldname):
					item[fieldname] = item["total_average_totals"][fieldname]

			# Item Wise wastage percentage is based on the aggregated values shown
			# in the row, rather than the stored percentage from each Stock Entry.
			item["wastage_percent"] = calculate_item_wise_wastage_percent(item)

		item.pop("posting_dates", None)
		item.pop("average_totals", None)
		item.pop("average_counts", None)
		item.pop("text_values", None)
		item.pop("size_values", None)
		data.append(item)

	data = sorted(
		data,
		key=lambda row: (
			row.get("date") or "",
			row.get("stock_entry") or "",
			row.get("detail_idx") or 0,
			row.get("item_name") or "",
			row.get("machine_name") or "",
			row.get("warehouse") or "",
		),
	)

	return data



def add_combined_total_row(data: list[dict], filters: frappe._dict) -> None:
	if not data:
		return

	total_row = {"item_code": _("Total"), "is_total_row": 1, "bold": 1}
	for fieldname in TOTAL_SUM_FIELDS:
		total_row[fieldname] = round(sum(flt(row.get(fieldname)) for row in data), 2)

	for fieldname in TOTAL_AVERAGE_FIELDS:
		if fieldname == "act_gsm":
			values = [flt(row.get(fieldname)) for row in data if flt(row.get(fieldname))]
			total_row[fieldname] = round(sum(values) / len(values), 2) if values else 0
			continue
		total = sum(flt(row.get("total_average_totals", {}).get(fieldname)) for row in data)
		count = sum(flt(row.get("total_average_counts", {}).get(fieldname)) for row in data)
		total_row[fieldname] = round(total / count, 2) if count else 0

	total_row["wastage_difference"] = round(
		flt(total_row.get("weight_bridge_wastage")) - flt(total_row.get("wastage")), 2
	)
	if not is_entry_wise(filters):
		total_row["wastage_percent"] = calculate_item_wise_wastage_percent(total_row)

	for amount_field, percent_field in (
		("ld", "ld_percent"),
		("trim", "trim_percent"),
		("other", "other_percent"),
	):
		total_row[percent_field] = round(
			(flt(total_row.get(amount_field)) / flt(total_row.get("total_qty"))) * 100, 2
		) if flt(total_row.get("total_qty")) else 0

	total_row["prod_percent"] = round(
		(flt(total_row.get("act_mtr")) / flt(total_row.get("target_mtr"))) * 100, 2
	) if flt(total_row.get("target_mtr")) else 0
	total_row["d_time_percent"] = round(
		(flt(total_row.get("d_time")) / flt(total_row.get("mc_run"))) * 100, 2
	) if flt(total_row.get("mc_run")) else 0

	for row in data:
		row.pop("total_average_totals", None)
		row.pop("total_average_counts", None)

	data.append(total_row)


def calculate_item_wise_wastage_percent(row: dict) -> float:
	total_qty = flt(row.get("total_qty"))
	return round((flt(row.get("weight_bridge_wastage")) / total_qty) * 100, 6) if total_qty else 0

def get_empty_group(row: frappe._dict, report_fields: list[dict], filters: frappe._dict) -> dict:
	item = {
		"date": row.date,
		"item_code": row.item_code,
		"item_name": row.item_name,
		"machine_name": row.machine_name,
		"warehouse": row.warehouse,
		# "purpose": row.purpose,
		"posting_dates": set(),
		"average_totals": {},
		"average_counts": {},
		"total_average_totals": {fieldname: 0 for fieldname in TOTAL_AVERAGE_FIELDS},
		"total_average_counts": {fieldname: 0 for fieldname in TOTAL_AVERAGE_FIELDS},
		"text_values": {},
		"size_values": [],
	}

	if is_entry_wise(filters):
		item["stock_entry"] = row.name
		item["detail_idx"] = row.detail_idx

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

	# if "target_mtr" in fieldnames and item.get("mc_run"):
	# 	item["target_mtr"] = item["mc_run"] * 45

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
	if "act_gsm" in fieldnames:
		average_size = get_average(item.get("size_values", []))
		item["act_gsm"] = (
			((flt(item.get("total_qty")) / flt(item.get("act_mtr"))) * 39.37 * 1000) / average_size
			if flt(item.get("act_mtr")) and average_size
			else 0
		)
	# if "total_wastage" in fieldnames:
	# 	item["total_wastage"] = (
	# 		flt(item.get("ld")) + flt(item.get("trim")) + flt(item.get("other"))
	# 	)
	# if "act_gsm" in fieldnames:
	# 	item["act_gsm"] = (
	# 		(flt(item.get("total_qty")) / flt(item.get("mtr"))) * 39.37 / 144 * 1000
	# 		if flt(item.get("mtr"))
	# 		else 0
	# 	)


def get_group_key(row: frappe._dict, filters: frappe._dict) -> tuple:
	if is_entry_wise(filters):
		return row.date, row.name, row.detail_name
	if is_date_range_item_wise(filters):
		return row.item_code, row.machine_name, row.warehouse
	return row.date, row.item_code, row.machine_name, row.warehouse


def get_warehouse_expression() -> str:
	return """
		case
			when ifnull(sed.is_finished_item, 0) = 1 then ifnull(sed.t_warehouse, sed.s_warehouse)
			else ifnull(sed.s_warehouse, sed.t_warehouse)
		end
	"""


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


# def add_text_value(values: list[str], value: str | None) -> None:
# 	value = (value or "").strip()
# 	if value and value not in values:
# 		values.append(value)

def add_text_value(values: list[str], value: str | None) -> None:
	if not value:
		return

	parts = []

	if isinstance(value, str):
		# Handle comma + newline separated values
		for row in value.split("\n"):
			for val in row.split(","):
				val = val.strip()

				# skip empty values
				if not val:
					continue

				# avoid duplicates
				if val not in parts:
					parts.append(val)

	for val in parts:
		if val not in values:
			values.append(val)


def get_numeric_values(value) -> list[float]:
	if value is None:
		return []

	values = []
	for part in str(value).replace("\n", ",").split(","):
		number = flt(part.strip())
		if number:
			values.append(number)
	return values


def get_average(values: list[float]) -> float:
	return sum(values) / len(values) if values else 0


def get_doc_field_sql(field: dict) -> str:
	if field.get("child_table") and field.get("child_value_field"):
		return f"max(ifnull({field['fieldname']}_values.value, '')) as {field['fieldname']}"

	if field["aggregate"] == "text":
		return (
			f"group_concat(distinct ifnull(se.{field['source']}, {get_sql_default(field)})) "
			f"as {field['fieldname']}"
		)

	return f"max(ifnull(se.{field['source']}, {get_sql_default(field)})) as {field['fieldname']}"


def get_table_multiselect_join(field: dict) -> str:
	return f"""
		left join (
			select
				parent,
				group_concat(distinct {field['child_value_field']} order by idx separator ', ') as value
			from `tab{field['child_table']}`
			where parenttype = 'Stock Entry'
				and parentfield = '{field['source']}'
			group by parent
		) {field['fieldname']}_values on {field['fieldname']}_values.parent = se.name"""


def get_table_multiselect_value_field(child_table: str | None) -> str | None:
	if not child_table:
		return None

	meta = frappe.get_meta(child_table)
	for field in meta.fields:
		if field.fieldtype == "Link":
			return field.fieldname

	return None


def get_column_fieldtype(field: dict) -> str:
	if field["aggregate"] == "text":
		return "Data"
	return field["fieldtype"] if field["fieldtype"] in NUMERIC_FIELDTYPES else "Float"


def get_column_width(field: dict) -> int:
	return 180 if field["aggregate"] == "text" else 120


def get_sql_default(field: dict) -> str:
	return "''" if field["aggregate"] == "text" else "0"
