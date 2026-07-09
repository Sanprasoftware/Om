import frappe

def update_purchase_receipt_qc_status(doc, method):
    if doc.reference_type == "Purchase Receipt" and doc.reference_name:
        frappe.db.set_value("Purchase Receipt",doc.reference_name,"custom_qc_status",doc.status
    )
        
def set_readings_status(doc, method=None):
    if doc.readings and doc.status:
        for row in doc.readings:
            row.status = doc.status