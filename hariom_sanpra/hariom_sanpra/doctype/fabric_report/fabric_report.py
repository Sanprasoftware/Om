# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, flt, getdate

from hariom_sanpra.hariom_sanpra.report.stock_balance_hariom.stock_balance_hariom import (
	StockBalanceReport,
)


DEFAULT_OUTPUT_FACTOR = 0.65


class FabricReport(Document):
	def validate(self):
		self._set_table_totals("fabric_stock_items", ("6ft_kg", "10_ft_kg", "11_ft_kg", "12_ft_kg"), "totalkg", "f_goutput_kg", "gsm")
		self._set_table_totals("unlam_sulzer_fabric_items", ("6ft_kg", "10_ft_kg", "12_ft_kg"), "totalkg", "f_goutput_kg", "gsm")
		self._set_table_totals("unlam__other_pond_fabric_items", ("6ft_kg", "10_ft_kg", "11_ft_kg", "12_ft_kg"), "totalkg", "f_goutput_kg", "gsm")
		self._set_table_totals("unlam_pipe_stock_items", ("6ft_kg", "75_ft_kg", "83_ft_kg"), "totalkg", "f_goutput_kg", "gsm")
		self._set_table_totals("pp_export_unlam__fab_stock_items", ("12_ft", "83_ft"), "totalkg", "f_g_outputkg", "gsm__fab")
		self._set_table_totals("pp_export_non_stock_items", ("qty_kg",), "total_kg", "fg__output_kg", "gsm")

	def _set_table_totals(self, table_field, quantity_fields, total_field, output_field, gsm_field):
		for row in self.get(table_field) or []:
			total = flt(sum(flt(row.get(fieldname)) for fieldname in quantity_fields), 2)
			divisor = _get_output_divisor(table_field, row.get(gsm_field), row.get("feet"))
			row.set(total_field, total)
			row.set(output_field, flt(total / divisor, 2))


@frappe.whitelist()
def get_fabric_stock(gsm, report_date=None, feet=None):
	"""Return Stock Balance Hariom closing stock for a GSM, grouped by fabric width."""
	stock = _empty_stock()
	if not gsm:
		return stock

	item_filters = {"custom_gsm1": gsm, "disabled": 0, "is_stock_item": 1}
	if feet:
		item_filters["custom_feet"] = feet

	items = frappe.get_all(
		"Item",
		filters=item_filters,
		fields=["name", "custom_feet"],
	)
	if not items:
		return stock

	feet_by_item = {item.name: _normalise_feet(item.custom_feet) for item in items}
	to_date = getdate(report_date)
	filters = frappe._dict(
		company=frappe.defaults.get_user_default("Company")
		or frappe.db.get_single_value("Global Defaults", "default_company"),
		from_date=add_months(to_date, -1),
		to_date=to_date,
		gsm=gsm,
		item_code=list(feet_by_item),
		ignore_closing_balance=0,
		include_zero_stock_items=0,
		show_stock_ageing_data=0,
		show_variant_attributes=0,
		show_dimension_wise_stock=0,
	)
	stock_report = StockBalanceReport(filters)
	stock_report.run()
	for row in stock_report.data:
		width = feet_by_item.get(row.item_code)
		if width:
			stock[width] = stock.get(width, 0.0) + flt(row.bal_qty)

	for width in stock:
		stock[width] = flt(stock[width])

	stock["qty_kg"] = stock.get(_normalise_feet(feet), 0.0) if feet else 0.0
	stock["total_kg"] = stock["qty_kg"]
	stock["fg__output_kg"] = flt(stock["total_kg"] / _get_output_divisor("pp_export_non_stock_items", gsm, feet), 2)
	return stock


def _empty_stock():
	return {
		"6": 0.0,
		"7.5": 0.0,
		"8.3": 0.0,
		"10": 0.0,
		"11": 0.0,
		"12": 0.0,
	}


def _normalise_feet(value):
	# FEET values may be saved as "8.3", "8.3 FT", "83 FT", and so on.
	feet = str(value or "").upper().replace("FEET", "").replace("FT", "").replace(" ", "").strip()
	aliases = {"6.0": "6", "7.50": "7.5", "75": "7.5", "8.30": "8.3", "83": "8.3", "10.0": "10", "11.0": "11", "12.0": "12"}
	return aliases.get(feet, feet or None)


def _get_output_divisor(table_field, gsm, feet=None):
	gsm = (gsm or "").strip().upper()

	if table_field == "unlam_sulzer_fabric_items" and gsm == "245 SULZER":
		return 0.60

	if table_field == "unlam_pipe_stock_items":
		if gsm in {"58 GSM","55 GSM", "60 GSM"}:
			return 0.50
		if gsm in {"75 GSM", "55 BLUE CHEX"}:
			return 0.45

	if table_field == "pp_export_unlam__fab_stock_items":
		return 0.42

	if table_field == "pp_export_non_stock_items":
		if gsm == "22 GSM BLACK" and _normalise_feet(feet) == "8.3":
			return 0.65
		if gsm == "22 GSM BLUE ARA":
			return 0.17
		if gsm in {
			"22 GSM BLACK",
			"22 GSM BLUE/2191",
			"22 GSM NEW CASTLE",
			"20/22 GSM COOL GREY",
			"45 GSM WHITE",
			"45 GSM CANVAS",
		}:
			return 0.23

	return DEFAULT_OUTPUT_FACTOR
