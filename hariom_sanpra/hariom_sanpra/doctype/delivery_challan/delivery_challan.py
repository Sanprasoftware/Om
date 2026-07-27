# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class deliverychallan(Document):

	def validate(self):
		self.calculate_amounts()

	def before_save(self):
		if self.type == "IN":
			self.status = ""

	def on_update(self):
		if self.type == "IN" and self.docstatus == 0 and self.ref_doc:
			self.update_ref_doc_status("Partially")

	def before_submit(self):
		if self.type == "OUT":
			self.set_pending_status()
		else:
			self.status = ""
	
	def calculate_amounts(self):
		for item in self.items:
			if item.qty and item.rate:
				item.amount = item.qty * item.rate

	def on_submit(self):
		if self.type == "IN":
			self.validate_in_qty()
		self.create_stock_entry()
#************************************************************************************************
	def set_pending_status(self):
		self.status = "Pending"
		for row in self.items:
			row.remaining_qty = row.qty
			row.status = "Pending"

	def update_ref_doc_status(self, status):
		frappe.db.set_value("delivery challan", self.ref_doc, "status", status)

	def validate_in_qty(self):
		if self.type != "IN":
			return

		if not self.ref_doc:
			frappe.throw(_("Reference Document not found"))

		ref_doc = frappe.get_doc("delivery challan", self.ref_doc)
		is_partially = False
		is_completed = True
		
		for in_row in self.items:
			found = False
			for ref_row in ref_doc.items:
				if in_row.item_code == ref_row.item_code:
					found = True
					available_qty = (
						ref_row.remaining_qty
						if ref_row.remaining_qty is not None
						else ref_row.qty
					)
					if in_row.qty > available_qty:
						frappe.throw(
							_(
								"Row {0}: Qty for Item {1} cannot be greater than Available Qty {2}"
							).format(
								in_row.idx,
								in_row.item_code,
								available_qty
							)
						)

					new_remaining_qty = available_qty - in_row.qty
					ref_row.remaining_qty = new_remaining_qty
					if new_remaining_qty == 0:
						ref_row.status = "Completed"
					else:
						ref_row.status = "Partially"
						is_completed = False

					if new_remaining_qty < ref_row.qty:
						is_partially = True

					ref_row.db_update()
			if not found:
				frappe.throw(
					_("Item {0} not found in Reference Document")
					.format(in_row.item_code)
				)

		for ref_row in ref_doc.items:
			if ref_row.remaining_qty:
				is_completed = False

		if is_completed:
			ref_doc.status = "Completed"
		elif is_partially:
			ref_doc.status = "Partially"
		else:
			ref_doc.status = "Pending"

		ref_doc.db_update()
		ref_doc.reload()

	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Material Transfer"
		# se.company = self.company
		for row in self.items:
			se.append("items", {
				"item_code": row.item_code,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"is_finished_item": row.is_finished_item,  
				"is_scrap_item": row.is_scrap_item,
			})
		se.save()
		# se.insert(ignore_permissions=True)
		# se.submit()
