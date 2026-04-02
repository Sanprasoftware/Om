import frappe

@frappe.whitelist()
def set_bom(doc, method=None):
    if not doc.custom_link_to_main_product:
        return

    item = frappe.get_doc("Item", doc.custom_link_to_main_product)

    # Check if already exists
    already_exists = False
    for row in item.custom_link_bom:
        if row.bom == doc.name:
            already_exists = True
            break

    # Append only if not exists
    if not already_exists:
        item.append("custom_link_bom", {
            "bom": doc.name,
            "item_code": doc.item
        })
        item.save(ignore_permissions=True)