import frappe

def notify_assigned_user(doc, method):
    # Sirf Purchase Receipt ke liye
    if doc.reference_type != "Purchase Receipt":
        return

    frappe.get_doc({
        "doctype": "Notification Log",
        "subject": f"Purchase Receipt {doc.reference_name} has been assigned to you.",
        "for_user": doc.allocated_to,
        "type": "Alert",
        "document_type": "Purchase Receipt",
        "document_name": doc.reference_name
    }).insert(ignore_permissions=True)