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
            "label": _("Assignment Date"),
            "fieldname": "assignment_date",
            "fieldtype": "Date",
            "width": 180
        },
        {
            "label": _("Quality Person"),
            "fieldname": "quality_person",
            "fieldtype": "Link",
            "options": "User",
            "width": 180
        },
        {
            "label": _("Reference Type"),
            "fieldname": "reference_type",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Assigned Count"),
            "fieldname": "assigned_count",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Pending Count"),
            "fieldname": "pending_count",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "label": _("Assigned IDs"),
            "fieldname": "assigned_ids",
            "fieldtype": "Small Text",
            "width": 300
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Pending IDs"),
            "fieldname": "pending_ids",
            "fieldtype": "Small Text",
            "width": 300
        }
    ]


# def get_data(filters):
#     data = []

#     notification_filters = {}

#     if filters.get("from_date") and filters.get("to_date"):
#         notification_filters["creation"] = [
#             "between",
#             [filters.get("from_date"), filters.get("to_date")]
#         ]

#     if filters.get("quality_person"):
#         notification_filters["for_user"] = filters.get("quality_person")
#     notification_filters["type"] = "Assignment"

#     notifications = frappe.get_all(
#         "Notification Log",
#         filters=notification_filters,
#         fields=[
#             "document_type",
#             "document_name",
#             "for_user",
#             "type"
#         ]
#     )

#     user_data = {}

#     for n in notifications:

#         if n.for_user not in user_data:
#             user_data[n.for_user] = {
#                 "Purchase Receipt": {
#                 "assigned": 0,
#                 "pending": 0,
#                 "assigned_ids": [],
#                 "pending_ids": []
#             },
#             "Delivery Note": {
#                 "assigned": 0,
#                 "pending": 0,
#                 "assigned_ids": [],
#                 "pending_ids": []
#             }
#             }

#         if n.document_type not in ["Purchase Receipt", "Delivery Note"]:
#             continue
				
#         if n.document_type == "Purchase Receipt":
#             user_data[n.for_user]["Purchase Receipt"]["assigned"] += 1
#             user_data[n.for_user]["Purchase Receipt"]["assigned_ids"].append(n.document_name)

#             qi = frappe.db.get_value(
#                 "Quality Inspection",
#                 {
#                     "reference_type": "Purchase Receipt",
#                     "reference_name": n.document_name
#                 },
#                 ["status"],
#                 as_dict=True
#             )

#             if not qi or qi.status != "Accepted":
#                 user_data[n.for_user]["Purchase Receipt"]["pending"] += 1
#                 user_data[n.for_user]["Purchase Receipt"]["pending_ids"].append(n.document_name)

#         elif n.document_type == "Delivery Note":
#             user_data[n.for_user]["Delivery Note"]["assigned"] += 1
#             user_data[n.for_user]["Delivery Note"]["assigned_ids"].append(n.document_name)

#             qi = frappe.db.get_value(
#                 "Quality Inspection",
#                 {
#                     "reference_type": "Delivery Note",
#                     "reference_name": n.document_name
#                 },
#                 ["status"],
#                 as_dict=True
#             )

#             if not qi or qi.status != "Accepted":
#                 user_data[n.for_user]["Delivery Note"]["pending"] += 1
#                 user_data[n.for_user]["Delivery Note"]["pending_ids"].append(n.document_name)

#     for user, refs in user_data.items():

#         data.append({
#             "quality_person": user,
#             "reference_type": "Purchase Receipt",
#             "assigned_count": refs["Purchase Receipt"]["assigned"],
#             "pending_count": refs["Purchase Receipt"]["pending"],
#             "assigned_ids": ", ".join(refs["Purchase Receipt"]["assigned_ids"]),
#             "pending_ids": ", ".join(refs["Purchase Receipt"]["pending_ids"]),
#         })

#         data.append({
#             "quality_person": user,
#             "reference_type": "Delivery Note",
#             "assigned_count": refs["Delivery Note"]["assigned"],
#             "pending_count": refs["Delivery Note"]["pending"],
#             "assigned_ids": ", ".join(refs["Delivery Note"]["assigned_ids"]),
#             "pending_ids": ", ".join(refs["Delivery Note"]["pending_ids"])
#         })

#     return data


def get_data(filters):
    data = []

    notification_filters = {
        "type": "Assignment"
    }

    if filters.get("from_date") and filters.get("to_date"):
        notification_filters["creation"] = [
            "between",
            [filters.get("from_date"), filters.get("to_date")]
        ]

    if filters.get("quality_person"):
        notification_filters["for_user"] = filters.get("quality_person")

    notifications = frappe.get_all(
        "Notification Log",
        filters=notification_filters,
        fields=[
            "document_type",
            "document_name",
            "for_user",
            "creation"
        ]
    )

    for n in notifications:

        if n.document_type not in ["Purchase Receipt", "Delivery Note"]:
            continue

        qi = frappe.db.get_value(
            "Quality Inspection",
            {
                "reference_type": n.document_type,
                "reference_name": n.document_name
            },
            ["status"],
            as_dict=True
        )

        status = qi.status if qi else "Not Created"

        data.append({
            "quality_person": n.for_user,
            "reference_type": n.document_type,
            "assignment_date": n.creation,
            "assigned_count": 1,
            "pending_count": 0 if status == "Accepted" else 1,
            "assigned_ids": n.document_name,
            "status": status,
            "pending_ids": "" if status == "Accepted" else n.document_name,
        })

    return data