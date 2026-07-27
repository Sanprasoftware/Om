import frappe
from frappe.utils import cint, cstr


REFERENCE_STATUS_FIELDS = {
    "Purchase Receipt": "custom_qc_status",
    "Delivery Note": "custom_quality_status",
}


def update_reference_qc_status(doc, method=None):
    status_field = REFERENCE_STATUS_FIELDS.get(doc.reference_type)
    if not status_field or not doc.reference_name:
        return

    status = "Cancelled" if method == "on_cancel" else doc.status
    frappe.db.set_value(doc.reference_type, doc.reference_name, status_field, status)

def set_readings_status(doc, method=None):
    if doc.readings and doc.status:
        for row in doc.readings:
            row.status = doc.status


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def item_query(doctype, txt, searchfield, start, page_len, filters):
    from_doctype = cstr(filters.get("from"))

    if from_doctype != "Purchase Receipt Item":
        from erpnext.stock.doctype.quality_inspection.quality_inspection import item_query as standard_item_query

        return standard_item_query(doctype, txt, searchfield, start, page_len, filters)

    parent = filters.get("parent")
    if not parent:
        return []

    if not frappe.has_permission("Purchase Receipt", "read", parent):
        frappe.throw(
            frappe._("Insufficient Permission for {0}").format(frappe.bold("Purchase Receipt")),
            frappe.PermissionError,
        )

    return frappe.db.sql(
        f"""
            SELECT distinct item_code, item_name
            FROM `tabPurchase Receipt Item`
            WHERE parent = %(parent)s
                and docstatus < 2
                and item_code like %(txt)s
                and (quality_inspection is null or quality_inspection = '')
            ORDER BY item_code
            limit {cint(page_len)} offset {cint(start)}
        """,
        {"parent": parent, "txt": f"%{txt}%"},
    )
