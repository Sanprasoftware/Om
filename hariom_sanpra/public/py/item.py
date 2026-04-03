# import frappe


# def create_new_item(doc, method=None):
#     if doc.custom_item_process:
#         for row in doc.custom_item_process:
#             new_doc = frappe.new_doc("Item")
#             new_doc.item_code = f"{doc.item_code}-{row.operation}"
#             new_doc.item_name = f"{doc.item_code}-{row.operation}"
#             new_doc.item_group = doc.item_group
#             new_doc.gst_hsn_code = doc.gst_hsn_code
#             new_doc.stock_uom = doc.stock_uom
#             new_doc.is_stock_item = 1
#             new_doc.save()
            

# import frappe

# def create_new_item(doc, method=None):

#     if " - " in doc.item_code:
#         return

#     if doc.custom_item_process:
#         for row in doc.custom_item_process:
#             item_code = doc.item_code
#             item_name = row.operation

#             new_item_code = item_code + " - " + item_name

#             new_doc = frappe.copy_doc(doc)

#             new_doc.item_code = new_item_code
#             new_doc.item_name = new_item_code

#             new_doc.insert(ignore_permissions=True)