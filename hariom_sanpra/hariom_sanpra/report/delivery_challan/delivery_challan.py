import frappe
from frappe import _


def execute(filters):
    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {
            "label": _("ID"),
            "fieldname": "delivery_challan",
            "fieldtype": "Link",
            "options": "delivery challan",
            "width": 180,
        },
        {
            "label": _("Date"),
            "fieldname": "date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Party Name"),
            "fieldname": "party_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Delivery Type"),
            "fieldname": "delivery_type",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Employee Name"),
            "fieldname": "employee_name",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
            "label": _("Qty"),
            "fieldname": "qty",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120,
        },
        # {
        #     "label": _("Time"),
        #     "fieldname": "time",
        #     "fieldtype": "Time",
        #     "width": 120,
        # },
        # {
        #     "label": _("Ref Doc"),
        #     "fieldname": "ref_doc",
        #     "fieldtype": "Data",
        #     "width": 180,
        # },
        # {
        #     "label": _("Source Warehouse"),
        #     "fieldname": "source_warehouse",
        #     "fieldtype": "Data",
        #     "width": 180,
        # },
        # {
        #     "label": _("Target Warehouse"),
        #     "fieldname": "target_warehouse",
        #     "fieldtype": "Data",
        #     "width": 180,
        # },
        # {
        #     "label": _("Remaining Qty"),
        #     "fieldname": "remaining_qty",
        #     "fieldtype": "Float",
        #     "width": 130,
        # },
        # {
        #     "label": _("Rate"),
        #     "fieldname": "rate",
        #     "fieldtype": "Currency",
        #     "width": 120,
        # },
        # {
        #     "label": _("Amount"),
        #     "fieldname": "amount",
        #     "fieldtype": "Currency",
        #     "width": 120,
        # },
    ]


def get_data(filters):
	filters = filters or {}

	filter = {
		"docstatus": ["!=", 0]
	}
	if filters.get("delivery_challan"):
		filter["name"] = filters.get("delivery_challan")
	if filters.get("from_date") and filters.get("to_date"):
		filter["date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
	delivery_challans = frappe.get_all(
		"delivery challan",
		filters=filter,
		fields=[
			"name as delivery_challan",
			"date",
			# "time",
			"party_name",
			"delivery_type",
			# "ref_doc"
		]
	)

	final_data = []

	for dc in delivery_challans:

		# Employee Names
		employee_ids = frappe.get_all(
			"Operator Name Items",
			filters={"parent": dc.delivery_challan},
			pluck="operator_name"
		)

		employee_names = []

		for emp in employee_ids:
			employee_name = frappe.db.get_value(
				"Employee",
				emp,
				"employee_name"
			)

			if employee_name:
				employee_names.append(employee_name)

		employee_name = ", ".join(employee_names)

		# Item Rows
		items = frappe.get_all(
			"delivery challan Items",
			filters={"parent": dc.delivery_challan},
			fields=[
				# "source_warehouse",
				# "target_warehouse",
				"item_code",
				"qty",
				"uom",
				# "remaining_qty",
				"status",
				# "rate",
				# "amount"
			]
		)

		for item in items:

			final_data.append({
				"delivery_challan": dc.delivery_challan,
				"date": dc.date,
				# "time": dc.time,
				"party_name": dc.party_name,
				"delivery_type": dc.delivery_type,
				"employee_name": employee_name,
				# "ref_doc": dc.ref_doc,
				# "source_warehouse": item.get("source_warehouse", ""),
				# "target_warehouse": item.get("target_warehouse", ""),
				"item_code": item.get("item_code", ""),
				"qty": item.get("qty", 0),
				"uom": item.get("uom", ""),
				# "remaining_qty": item.get("remaining_qty", 0),
				"status": item.get("status", ""),
				# "rate": item.get("rate", 0),
				# "amount": item.get("amount", 0),
			})

	return final_data