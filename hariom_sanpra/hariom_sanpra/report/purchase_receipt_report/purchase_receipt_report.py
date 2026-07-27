# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": _("ID"),
            "fieldname": "purchase_receipt_id",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 120,
        },
        {
            "label": _("Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 110,
        },
        {
            "label": _("Supplier"),
            "fieldname": "supplier",
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {
			"label": _("Item Name"),
			"fieldname": "item_name",  
			"fieldtype": "Data",     
			"width": 180,
		},
        {
			"label": _("Quantity"),
			"fieldname": "quantity",  
			"fieldtype": "Float",     
			"width": 100,
		},
        {
            "label": _("Batch No"),
            "fieldname": "batch_no",
            "fieldtype": "Link",
            "options": "Batch",
            "width": 150,
        },
        {
			"label": _("Rate"),
			"fieldname": "rate",  
			"fieldtype": "Float",     
			"width": 100,
		},
        {
			"label": _("Amount"),
			"fieldname": "amount",  
			"fieldtype": "Float",     
			"width": 100,
		},
        {
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 150,
        },
    ]


def get_data(filters):
    data = []

    pr_filters = {"docstatus": 1}

    if filters.get("from_date") and filters.get("to_date"):
        pr_filters["posting_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
    elif filters.get("from_date"):
        pr_filters["posting_date"] = [">=", filters.get("from_date")]
    elif filters.get("to_date"):
        pr_filters["posting_date"] = ["<=", filters.get("to_date")]

    if filters.get("purchase_receipt_id"):
        pr_filters["name"] = filters.get("purchase_receipt_id")

    if filters.get("supplier"):
        pr_filters["supplier"] = filters.get("supplier")

    purchase_receipts = frappe.get_all(
        "Purchase Receipt",
        filters=pr_filters,
        fields=["name", "posting_date", "supplier"]
    )

    for pr in purchase_receipts:
        doc = frappe.get_doc("Purchase Receipt", pr.name)
        first_row = True
        for item in doc.items:

            if filters.get("item_code") and item.item_code != filters.get("item_code"):
                continue

            if filters.get("item_group") and item.item_group != filters.get("item_group"):
                continue

            if filters.get("warehouse") and item.warehouse != filters.get("warehouse"):
                continue

            data.append({
                "purchase_receipt_id": pr.name if first_row else "",
                "posting_date": pr.posting_date if first_row else "",
                "supplier": pr.supplier if first_row else "",
                "item_code": item.item_code,
                "item_name": item.item_name,
                "quantity": item.qty,
                "batch_no": item.batch_no,
                "rate": item.rate,
                "amount": item.amount,
                "warehouse": item.warehouse if first_row else "",
            })
            first_row = False

    return data