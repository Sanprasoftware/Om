import frappe


def create_stock_entry(doc, method=None):
    if doc.custom_with_packing == 1 and doc.custom_packing_material:
        new_doc =  frappe.new_doc("Stock Entry")
        new_doc.stock_entry_type = "Material Issue"

        for row in doc.custom_packing_material:
            new_doc.append("items", {
            "s_warehouse": row.warehouse,
            "item_code": row.item_code,
            "qty":  row.qty
            })

        new_doc.save()