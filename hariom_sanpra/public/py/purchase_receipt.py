from frappe.utils import flt


def set_rejected_warehouse(doc, method=None):
	"""Set a rejected warehouse only for rows that contain rejected stock."""
	for row in doc.items:
		if not flt(row.rejected_qty):
			row.rejected_warehouse = None
		elif not row.rejected_warehouse and doc.rejected_warehouse:
			row.rejected_warehouse = doc.rejected_warehouse
