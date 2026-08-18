import frappe
from erpnext import get_default_company
from frappe.utils import add_days
from frappe.utils import add_months
from frappe.utils import flt
from frappe.utils import get_first_day
from frappe.utils import nowdate

from hariom_sanpra.hariom_sanpra.report.daily_cumulative_production_report.daily_cumulative_production_report import (
	execute as execute_daily_production,
)
from hariom_sanpra.hariom_sanpra.report.stock_balance_hariom.stock_balance_hariom import (
	execute as execute_stock_balance,
)


PRODUCTS = (
	{"label": "PONDLINE", "icon": "drop", "manufacturing_type": "PONDLINE", "semi_ready": ("PONDLINE FG - OM",), "ready_stock": ("GD REWINDING Ready To Dispatch - OM", "JOINT MACHINE Ready To Dispatch - OM")},
	{"label": "PIPE", "icon": "pipe", "manufacturing_type": "PIPE", "semi_ready": ("PIPE FG - OM",), "ready_stock": ("SMALL PIPE M/C Ready to dispatch - OM",)},
	{"label": "PP EXPORT", "icon": "box", "manufacturing_type": "PP EXPORT", "semi_ready": ("PP EXPORT FG - OM",), "ready_stock": ("NAVRANG-REWINDING M/C Ready To Dispatch - OM",)},
	{"label": "MURGHAS", "icon": "layers", "manufacturing_type": "JP M/C MURGHAS", "semi_ready": ("MURGHAS FG - OM",), "ready_stock": ()},
)


@frappe.whitelist()
def get_dashboard_data():
	"""Return current Stock Balance quantities for the production dashboard."""
	warehouses = {warehouse for product in PRODUCTS for stock_type in ("semi_ready", "ready_stock") for warehouse in product[stock_type]}
	balances = _get_warehouse_balances(warehouses)
	raw_material_days = _get_raw_material_days_left()
	return [
		{
			"label": product["label"],
			"icon": product["icon"],
			"raw_material_days": raw_material_days.get(product["manufacturing_type"]),
			"semi_ready": _quantity_in_tons(product["semi_ready"], balances),
			"ready_stock": _quantity_in_tons(product["ready_stock"], balances),
			"wastage_percent": _get_monthly_wastage_percent(product["manufacturing_type"]),
		}
		for product in PRODUCTS
	]


def _get_raw_material_days_left(consumption_days=30):
	today = nowdate()
	manufacturing_types = [product["manufacturing_type"] for product in PRODUCTS]
	raw_material_group = frappe.db.get_value(
		"Item Group", "Raw Material", ["lft", "rgt"], as_dict=True
	)
	if not raw_material_group:
		return {}

	consumption = frappe.db.sql(
		"""
		SELECT
			se.custom_manufacture_type AS manufacturing_type,
			sed.item_code,
			SUM(ABS(sed.transfer_qty)) AS consumed_qty
		FROM `tabStock Entry` se
		INNER JOIN `tabStock Entry Detail` sed ON sed.parent = se.name
		INNER JOIN `tabItem` item ON item.name = sed.item_code
		INNER JOIN `tabItem Group` item_group ON item_group.name = item.item_group
		WHERE se.docstatus = 1
			AND se.company = %(company)s
			AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s
			AND se.custom_manufacture_type IN %(manufacturing_types)s
			AND sed.s_warehouse IS NOT NULL
			AND COALESCE(sed.is_finished_item, 0) = 0
			AND item_group.lft >= %(raw_lft)s
			AND item_group.rgt <= %(raw_rgt)s
		GROUP BY se.custom_manufacture_type, sed.item_code
		""",
		{
			"company": get_default_company(),
			"from_date": add_days(today, -(consumption_days - 1)),
			"to_date": today,
			"manufacturing_types": manufacturing_types,
			"raw_lft": raw_material_group.lft,
			"raw_rgt": raw_material_group.rgt,
		},
		as_dict=True,
	)
	if not consumption:
		return {}

	item_codes = list({row.item_code for row in consumption})
	filters = frappe._dict(
		company=get_default_company(),
		from_date=add_months(today, -1),
		to_date=today,
		item_code=item_codes,
		show_stock_ageing_data=False,
		show_variant_attributes=False,
		show_dimension_wise_stock=False,
		ignore_closing_balance=False,
		include_zero_stock_items=False,
	)
	_columns, stock_rows = execute_stock_balance(filters)
	item_balances = {}
	for row in stock_rows:
		item_balances[row.item_code] = item_balances.get(row.item_code, 0) + flt(row.bal_qty)

	product_totals = {}
	for row in consumption:
		totals = product_totals.setdefault(row.manufacturing_type, {"stock": 0, "consumed": 0})
		totals["stock"] += max(item_balances.get(row.item_code, 0), 0)
		totals["consumed"] += flt(row.consumed_qty)

	return {
		manufacturing_type: flt(
			totals["stock"] / (totals["consumed"] / consumption_days), 1
		)
		for manufacturing_type, totals in product_totals.items()
		if totals["consumed"]
	}


def _get_monthly_wastage_percent(manufacturing_type):
	today = nowdate()
	_filters = frappe._dict(
		from_date=get_first_day(today),
		to_date=today,
		manufacturing_type=manufacturing_type,
		report_based_on="Item Wise",
	)
	_columns, data, *_rest = execute_daily_production(_filters)
	if not data or not data[-1].get("is_total_row"):
		return 0
	return flt(data[-1].get("wastage_percent"), 2)


def _get_warehouse_balances(warehouses):
	if not warehouses:
		return {}

	# Some existing Warehouse names contain repeated spaces/tabs before "- OM".
	# Match normalized names while retaining the clean labels requested for the UI.
	available_warehouses = frappe.get_all("Warehouse", pluck="name", limit_page_length=0)
	available_by_normalized_name = {
		_normalize_warehouse_name(warehouse): warehouse for warehouse in available_warehouses
	}
	resolved_warehouses = {
		warehouse: available_by_normalized_name.get(_normalize_warehouse_name(warehouse))
		for warehouse in warehouses
	}
	actual_warehouses = [warehouse for warehouse in resolved_warehouses.values() if warehouse]
	if not actual_warehouses:
		return {}

	_to_date = nowdate()
	filters = frappe._dict(
		company=get_default_company(),
		from_date=add_months(_to_date, -1),
		to_date=_to_date,
		warehouse=actual_warehouses,
		show_stock_ageing_data=False,
		show_variant_attributes=False,
		show_dimension_wise_stock=False,
		ignore_closing_balance=False,
		include_zero_stock_items=False,
	)
	_columns, rows = execute_stock_balance(filters)
	actual_balances = {}
	for row in rows:
		actual_balances[row.warehouse] = actual_balances.get(row.warehouse, 0) + flt(row.bal_qty)
	return {
		warehouse: actual_balances.get(actual_warehouse, 0)
		for warehouse, actual_warehouse in resolved_warehouses.items()
	}


def _normalize_warehouse_name(warehouse):
	return " ".join(warehouse.split()).casefold()


def _quantity_in_tons(warehouses, balances):
	if not warehouses:
		return None
	return flt(sum(balances.get(warehouse, 0) for warehouse in warehouses) / 1000, 3)
