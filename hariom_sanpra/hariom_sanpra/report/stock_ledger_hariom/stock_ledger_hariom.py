# # Copyright (c) 2026, Sanpra Software Solution and contributors
# # For license information, please see license.txt

# import frappe
# from frappe import _
# from frappe.utils import cint, flt, get_datetime

# from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
# from erpnext.stock.report.stock_ledger import stock_ledger as base_stock_ledger
# from erpnext.stock.utils import (
# 	is_reposting_item_valuation_in_progress,
# 	update_included_uom_in_report,
# )
 

# def execute(filters=None):
# 	is_reposting_item_valuation_in_progress()
# 	filters = frappe._dict(filters or {})

# 	include_uom = filters.get("include_uom")
# 	columns = base_stock_ledger.get_columns(filters)
# 	columns = remove_unwanted_columns(columns)
# 	columns = add_opening_qty_column(columns)
# 	items = base_stock_ledger.get_items(filters)
# 	sl_entries = get_stock_ledger_entries(filters, items)
# 	item_details = base_stock_ledger.get_item_details(items, sl_entries, include_uom)

# 	if filters.get("batch_no"):
# 		opening_row = base_stock_ledger.get_opening_balance_from_batch(filters, columns, sl_entries)
# 	else:
# 		opening_row = base_stock_ledger.get_opening_balance(filters, columns, sl_entries)

# 	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
# 	bundle_details = {}

# 	if filters.get("segregate_serial_batch_bundle"):
# 		bundle_details = base_stock_ledger.get_serial_batch_bundle_details(sl_entries, filters)

# 	data = []
# 	conversion_factors = []
# 	if opening_row:
# 		data.append(opening_row)
# 		conversion_factors.append(0)

# 	actual_qty = stock_value = 0
# 	if opening_row:
# 		actual_qty = opening_row.get("qty_after_transaction")
# 		stock_value = opening_row.get("stock_value")

# 	available_serial_nos = {}
# 	inventory_dimension_filters_applied = base_stock_ledger.check_inventory_dimension_filters_applied(
# 		filters
# 	)

# 	batch_balance_dict = frappe._dict({})
# 	if actual_qty and filters.get("batch_no"):
# 		batch_balance_dict[filters.batch_no] = [actual_qty, stock_value]

# 	for sle in sl_entries:
# 		item_detail = item_details[sle.item_code]

# 		sle.update(item_detail)
# 		if bundle_info := bundle_details.get(sle.serial_and_batch_bundle):
# 			data.extend(
# 				base_stock_ledger.get_segregated_bundle_entries(
# 					sle, bundle_info, batch_balance_dict, filters
# 				)
# 			)
# 			continue

# 		if filters.get("batch_no") or inventory_dimension_filters_applied:
# 			actual_qty += flt(sle.actual_qty, precision)
# 			stock_value += sle.stock_value_difference
# 			if sle.batch_no:
# 				if not batch_balance_dict.get(sle.batch_no):
# 					batch_balance_dict[sle.batch_no] = [0, 0]

# 				batch_balance_dict[sle.batch_no][0] += sle.actual_qty
# 				batch_balance_dict[sle.batch_no][1] += stock_value

# 			if filters.get("segregate_serial_batch_bundle"):
# 				actual_qty = batch_balance_dict[sle.batch_no][0]

# 			if sle.voucher_type == "Stock Reconciliation" and not sle.actual_qty:
# 				actual_qty = sle.qty_after_transaction
# 				stock_value = sle.stock_value

# 			sle.update({"qty_after_transaction": actual_qty, "stock_value": stock_value})

# 		sle.update({"in_qty": max(sle.actual_qty, 0), "out_qty": min(sle.actual_qty, 0)})

# 		if sle.serial_no:
# 			base_stock_ledger.update_available_serial_nos(available_serial_nos, sle)

# 		if sle.actual_qty:
# 			sle["in_out_rate"] = flt(sle.stock_value_difference / sle.actual_qty, precision)
# 		elif sle.voucher_type == "Stock Reconciliation":
# 			sle["in_out_rate"] = sle.valuation_rate

# 		sle["opening_qty"] = flt(sle.qty_after_transaction) - flt(sle.actual_qty)
# 		data.append(sle)

# 		if include_uom:
# 			conversion_factors.append(item_detail.conversion_factor)

# 	for row in data:
# 		if "actual_qty" in row:
# 			row["opening_qty"] = flt(row.get("qty_after_transaction")) - flt(row.get("actual_qty"))
# 		else:
# 			row["opening_qty"] = flt(row.get("qty_after_transaction"))

# 	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
# 	return columns, data


# def remove_unwanted_columns(columns):
# 	excluded_fields = {
# 		"item_name",
# 		"description",
# 		"incoming_rate",
# 		"valuation_rate",
# 		"in_out_rate",
# 		"stock_value",
# 		"serial_no",
# 		"project",
# 		"company",
# 		"voucher_type",
# 		"stock_value_difference",
# 		"item_group",
# 		"brand",
# 		"batch_no",
# 	}

# 	filtered_columns = []
# 	for column in columns:
# 		if column.get("fieldname") in excluded_fields:
# 			continue

# 		if column.get("fieldname") == "item_code":
# 			column["width"] = 380

# 		filtered_columns.append(column)

# 	return filtered_columns


# def add_opening_qty_column(columns):
# 	opening_qty_column = {
# 		"label": _("Opening Qty"),
# 		"fieldname": "opening_qty",
# 		"fieldtype": "Float",
# 		"width": 100,
# 		"convertible": "qty",
# 	}

# 	for idx, column in enumerate(columns):
# 		if column.get("fieldname") == "in_qty":
# 			return columns[:idx] + [opening_qty_column] + columns[idx:]

# 	return columns + [opening_qty_column]


# def get_stock_ledger_entries(filters, items):
# 	from_date = get_datetime(filters.from_date + " 00:00:00")
# 	to_date = get_datetime(filters.to_date + " 23:59:59")

# 	sle = frappe.qb.DocType("Stock Ledger Entry")
# 	query = (
# 		frappe.qb.from_(sle)
# 		.select(
# 			sle.item_code,
# 			sle.posting_datetime.as_("date"),
# 			sle.warehouse,
# 			sle.posting_date,
# 			sle.posting_time,
# 			sle.actual_qty,
# 			sle.incoming_rate,
# 			sle.valuation_rate,
# 			sle.company,
# 			sle.voucher_type,
# 			sle.qty_after_transaction,
# 			sle.stock_value_difference,
# 			sle.serial_and_batch_bundle,
# 			sle.voucher_no,
# 			sle.stock_value,
# 			sle.batch_no,
# 			sle.serial_no,
# 			sle.project,
# 		)
# 		.where((sle.docstatus < 2) & (sle.is_cancelled == 0) & (sle.posting_datetime[from_date:to_date]))
# 		.orderby(sle.posting_datetime)
# 		.orderby(sle.creation)
# 	)

# 	inventory_dimension_fields = base_stock_ledger.get_inventory_dimension_fields()
# 	if inventory_dimension_fields:
# 		for fieldname in inventory_dimension_fields:
# 			query = query.select(fieldname)
# 			if fieldname in filters and filters.get(fieldname):
# 				query = query.where(sle[fieldname].isin(filters.get(fieldname)))

# 	if items:
# 		query = query.where(sle.item_code.isin(items))

# 	for field in ["voucher_no", "project", "company"]:
# 		if filters.get(field) and field not in inventory_dimension_fields:
# 			query = query.where(sle[field] == filters.get(field))

# 	if filters.get("work_order"):
# 		voucher_nos = get_work_order_stock_entry_vouchers(filters.get("work_order"))
# 		if not voucher_nos:
# 			return []
# 		query = query.where((sle.voucher_type == "Stock Entry") & (sle.voucher_no.isin(voucher_nos)))

# 	if filters.get("batch_no"):
# 		bundles = base_stock_ledger.get_serial_and_batch_bundles(filters)

# 		if bundles:
# 			query = query.where(
# 				(sle.serial_and_batch_bundle.isin(bundles)) | (sle.batch_no == filters.batch_no)
# 			)
# 		else:
# 			query = query.where(sle.batch_no == filters.batch_no)

# 	query = apply_warehouse_filter(query, sle, filters)

# 	return query.run(as_dict=True)


# def get_work_order_stock_entry_vouchers(work_order):
# 	return frappe.get_all("Stock Entry", filters={"work_order": work_order}, pluck="name")



# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import cint, flt, get_datetime

from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
from erpnext.stock.report.stock_ledger import stock_ledger as base_stock_ledger
from erpnext.stock.utils import (
	is_reposting_item_valuation_in_progress,
	update_included_uom_in_report,
)


def execute(filters=None):
	is_reposting_item_valuation_in_progress()
	filters = frappe._dict(filters or {})

	include_uom = filters.get("include_uom")
	columns = base_stock_ledger.get_columns(filters)
	columns = remove_unwanted_columns(columns)
	columns = add_opening_qty_column(columns)

	items = base_stock_ledger.get_items(filters)
	sl_entries = get_stock_ledger_entries(filters, items)
	item_details = base_stock_ledger.get_item_details(items, sl_entries, include_uom)

	if filters.get("batch_no"):
		opening_row = base_stock_ledger.get_opening_balance_from_batch(filters, columns, sl_entries)
	else:
		opening_row = base_stock_ledger.get_opening_balance(filters, columns, sl_entries)

	precision = cint(frappe.db.get_single_value("System Settings", "float_precision"))
	bundle_details = {}

	if filters.get("segregate_serial_batch_bundle"):
		bundle_details = base_stock_ledger.get_serial_batch_bundle_details(sl_entries, filters)

	data = []
	conversion_factors = []

	if opening_row:
		opening_row["qty_after_transaction"] = round_qty(opening_row.get("qty_after_transaction"))
		opening_row["opening_qty"] = round_qty(opening_row.get("qty_after_transaction"))
		data.append(opening_row)
		conversion_factors.append(0)

	actual_qty = 0
	stock_value = 0

	if opening_row:
		actual_qty = round_qty(opening_row.get("qty_after_transaction"))
		stock_value = opening_row.get("stock_value")

	available_serial_nos = {}

	# inventory_dimension_filters_applied = base_stock_ledger.check_inventory_dimension_filters_applied(
	# 	filters
	# )

	inventory_dimension_filters_applied = False

	batch_balance_dict = frappe._dict({})

	if actual_qty and filters.get("batch_no"):
		batch_balance_dict[filters.batch_no] = [actual_qty, stock_value]

	for sle in sl_entries:
		item_detail = item_details[sle.item_code]
		sle.update(item_detail)

		if bundle_info := bundle_details.get(sle.serial_and_batch_bundle):
			data.extend(
				base_stock_ledger.get_segregated_bundle_entries(
					sle, bundle_info, batch_balance_dict, filters
				)
			)
			continue

		if filters.get("batch_no") or inventory_dimension_filters_applied:
			actual_qty += round_qty(sle.actual_qty)
			stock_value += sle.stock_value_difference

			if sle.batch_no:
				if not batch_balance_dict.get(sle.batch_no):
					batch_balance_dict[sle.batch_no] = [0, 0]

				batch_balance_dict[sle.batch_no][0] += round_qty(sle.actual_qty)
				batch_balance_dict[sle.batch_no][1] += stock_value

			if filters.get("segregate_serial_batch_bundle"):
				actual_qty = batch_balance_dict[sle.batch_no][0]

			if sle.voucher_type == "Stock Reconciliation" and not sle.actual_qty:
				actual_qty = round_qty(sle.qty_after_transaction)
				stock_value = sle.stock_value

			sle.update({
				"qty_after_transaction": round_qty(actual_qty),
				"stock_value": stock_value
			})

		sle.update({
			"in_qty": round_qty(max(sle.actual_qty, 0)),
			"out_qty": round_qty(min(sle.actual_qty, 0))
		})

		if sle.serial_no:
			base_stock_ledger.update_available_serial_nos(available_serial_nos, sle)

		if sle.actual_qty:
			sle["in_out_rate"] = flt(sle.stock_value_difference / sle.actual_qty, precision)
		elif sle.voucher_type == "Stock Reconciliation":
			sle["in_out_rate"] = sle.valuation_rate

		sle["opening_qty"] = round_qty(round_qty(sle.qty_after_transaction) - round_qty(sle.actual_qty))

		sle["qty_after_transaction"] = round_qty(sle.qty_after_transaction)

		data.append(sle)

		if include_uom:
			conversion_factors.append(item_detail.conversion_factor)

	for row in data:
		if "actual_qty" in row:
			row["opening_qty"] = round_qty(
				round_qty(row.get("qty_after_transaction")) - round_qty(row.get("actual_qty"))
			)
		else:
			row["opening_qty"] = round_qty(row.get("qty_after_transaction"))

		row["in_qty"] = round_qty(row.get("in_qty", 0))
		row["out_qty"] = round_qty(row.get("out_qty", 0))
		row["qty_after_transaction"] = round_qty(row.get("qty_after_transaction", 0))
		row["stock_uom"] = item_details.get(row.get("item_code"), {}).get("stock_uom", "")

	update_included_uom_in_report(columns, data, include_uom, conversion_factors)
	columns = add_stock_uom_column(columns)
	return columns, data


def remove_unwanted_columns(columns):
	excluded_fields = {
		"item_name",
		"description",
		"incoming_rate",
		"valuation_rate",
		"in_out_rate",
		"stock_value",
		"serial_no",
		"project",
		"company",
		"voucher_type",
		"stock_value_difference",
		"item_group",
		"brand",
		"batch_no",
		"stock_uom",
	}

	filtered_columns = []

	for column in columns:
		if column.get("fieldname") in excluded_fields:
			continue

		if column.get("fieldname") == "item_code":
			column["width"] = 380
		elif column.get("fieldname") in {"opening_qty", "in_qty", "out_qty", "qty_after_transaction"}:
			column["fieldtype"] = "Int"

		filtered_columns.append(column)

	return filtered_columns


def add_opening_qty_column(columns):
	opening_qty_column = {
		"label": _("Opening Qty"),
		"fieldname": "opening_qty",
		"fieldtype": "Int",
		"width": 100,
		"convertible": "qty",
	}

	for idx, column in enumerate(columns):
		if column.get("fieldname") == "in_qty":
			return columns[:idx] + [opening_qty_column] + columns[idx:]

	return columns + [opening_qty_column]

def add_stock_uom_column(columns):
	stock_uom_column = {
		"label": _("Stock UOM"),
		"fieldname": "stock_uom",
		"fieldtype": "Link",
		"options": "UOM",
		"width": 100,
	}
	return columns + [stock_uom_column]

def get_stock_ledger_entries(filters, items):
	from_date = get_datetime(filters.from_date + " 00:00:00")
	to_date = get_datetime(filters.to_date + " 23:59:59")

	sle = frappe.qb.DocType("Stock Ledger Entry")

	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item_code,
			sle.posting_datetime.as_("date"),
			sle.warehouse,
			sle.posting_date,
			sle.posting_time,
			sle.actual_qty,
			sle.incoming_rate,
			sle.valuation_rate,
			sle.company,
			sle.voucher_type,
			sle.qty_after_transaction,
			sle.stock_value_difference,
			sle.serial_and_batch_bundle,
			sle.voucher_no,
			sle.stock_value,
			sle.batch_no,
			sle.serial_no,
			sle.project,
			
		)
		.where((sle.docstatus < 2) & (sle.is_cancelled == 0) & (sle.posting_datetime[from_date:to_date]))
		.orderby(sle.posting_datetime)
		.orderby(sle.creation)
	)

	inventory_dimension_fields = base_stock_ledger.get_inventory_dimension_fields()

	if inventory_dimension_fields:
		for fieldname in inventory_dimension_fields:
			query = query.select(fieldname)
			if fieldname in filters and filters.get(fieldname):
				query = query.where(sle[fieldname].isin(filters.get(fieldname)))

	if items:
		query = query.where(sle.item_code.isin(items))

	for field in ["voucher_no", "project", "company"]:
		if filters.get(field) and field not in inventory_dimension_fields:
			query = query.where(sle[field] == filters.get(field))

	if filters.get("work_order"):
		voucher_nos = get_work_order_stock_entry_vouchers(filters.get("work_order"))
		if not voucher_nos:
			return []
		query = query.where((sle.voucher_type == "Stock Entry") & (sle.voucher_no.isin(voucher_nos)))

	if filters.get("batch_no"):
		bundles = base_stock_ledger.get_serial_and_batch_bundles(filters)

		if bundles:
			query = query.where(
				(sle.serial_and_batch_bundle.isin(bundles)) | (sle.batch_no == filters.batch_no)
			)
		else:
			query = query.where(sle.batch_no == filters.batch_no)

	query = apply_warehouse_filter(query, sle, filters)

	return query.run(as_dict=True)


def get_work_order_stock_entry_vouchers(work_order):
	return frappe.get_all("Stock Entry", filters={"work_order": work_order}, pluck="name")


def round_qty(value):
	return int(flt(value, 0))
