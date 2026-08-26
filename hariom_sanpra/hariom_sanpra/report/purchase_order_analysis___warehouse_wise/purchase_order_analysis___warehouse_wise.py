import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions
from erpnext.buying.report.purchase_order_analysis import purchase_order_analysis


def execute(filters=None):
	if not filters:
		return [], []

	purchase_order_analysis.validate_filters(filters)

	columns = purchase_order_analysis.get_columns(filters)
	data = purchase_order_analysis.get_data(filters)
	data = filter_by_warehouse_user_permissions(data)

	if not data:
		return [], [], None, []

	purchase_order_analysis.update_received_amount(data)
	data, chart_data = purchase_order_analysis.prepare_data(data, filters)

	return columns, data, None, chart_data


def filter_by_warehouse_user_permissions(data):
	"""Keep only POs allowed by Warehouse User Permissions applicable to Purchase Order."""
	warehouse_permissions = get_user_permissions(frappe.session.user).get("Warehouse", [])
	allowed_warehouses = {
		permission.doc
		for permission in warehouse_permissions
		if not permission.applicable_for or permission.applicable_for == "Purchase Order"
	}

	if not allowed_warehouses:
		return data

	return [row for row in data if row.warehouse in allowed_warehouses]
