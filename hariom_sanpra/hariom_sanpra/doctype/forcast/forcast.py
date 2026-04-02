# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import calendar
import json

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.query_builder.functions import Sum
from frappe.utils import flt, getdate, today


class Forcast(Document):
	def validate(self):
		self._set_program_pending(self.forcast_item)
		self._set_program_pending(self.lamination)
		self.total_plan_fg = self._get_rows_total(self.forcast_item, "fg_output_ton") + self._get_rows_total(
			self.lamination, "fg_output_ton"
		)
		self.total_fg = self._get_rows_total(self.forcast_item, "program_complete") + self._get_rows_total(
			self.lamination, "program_complete"
		)
		self.total_working_days = self._get_rows_total(
			self.forcast_item, "work_days"
		) + self._get_rows_total(self.lamination, "work_days")

	def _set_program_pending(self, rows):
		for row in rows or []:
			row.program_pending = flt(row.fg_output_ton) - flt(row.program_complete)

	def _get_rows_total(self, rows, fieldname):
		return sum(flt(row.get(fieldname)) for row in rows or [])


@frappe.whitelist()
def get_stock_for_items(doc):
	if isinstance(doc, str):
		doc = json.loads(doc)

	month = doc.get("month")
	if not month:
		frappe.throw(_("Month is required to get stock."))

	year = getdate(doc.get("date") or today()).year
	from_date, to_date = _get_month_date_range(year, month)

	item_codes = {
		row.get("item_code")
		for tablefield in ("forcast_item", "lamination")
		for row in (doc.get(tablefield) or [])
		if row.get("item_code")
	}

	stock_map = _get_item_stock_map(item_codes, from_date, to_date)
	row_stock_map = {}

	for tablefield in ("forcast_item", "lamination"):
		for row in doc.get(tablefield) or []:
			row_stock_map[row.get("name")] = flt(stock_map.get(row.get("item_code")))

	return row_stock_map


def _get_month_date_range(year, month):
	month_index = {
		"JAN": 1,
		"FEB": 2,
		"MAR": 3,
		"APR": 4,
		"MAY": 5,
		"JUN": 6,
		"JUL": 7,
		"AUG": 8,
		"SEP": 9,
		"OCT": 10,
		"NOV": 11,
		"DEC": 12,
	}.get((month or "").upper())

	if not month_index:
		frappe.throw(_("Invalid month selected."))

	last_day = calendar.monthrange(year, month_index)[1]
	return f"{year}-{month_index:02d}-01", f"{year}-{month_index:02d}-{last_day:02d}"


def _get_item_stock_map(item_codes, from_date, to_date):
	if not item_codes:
		return {}

	sle = frappe.qb.DocType("Stock Ledger Entry")
	rows = (
		frappe.qb.from_(sle)
		.select(sle.item_code, Sum(sle.actual_qty).as_("stock_qty"))
		.where(sle.item_code.isin(list(item_codes)))
		.where(sle.posting_date >= from_date)
		.where(sle.posting_date <= to_date)
		.where(sle.is_cancelled == 0)
		.groupby(sle.item_code)
	).run(as_dict=True)

	return {row.item_code: flt(row.stock_qty) for row in rows}
