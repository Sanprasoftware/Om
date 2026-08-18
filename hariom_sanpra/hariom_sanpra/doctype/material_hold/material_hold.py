# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class MaterialHold(Document):
	def on_submit(self):
		self.create_stock_entry()

	def on_cancel(self):
		self.cancel_stock_entry()

	def on_trash(self):
		self.delete_stock_entry()

	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = self.stock_entry_type
		se.set_posting_time = 1
		se.posting_date = self.date
		se.custom_reference_doc = self.doctype
		se.custom_reference_id = self.name
		for row in self.items:
			se.append("items", {
				"item_code": row.item_code,
				"qty": row.qty,
				"uom": row.uom,
				"use_serial_batch_fields":row.use_serial_no__batch_fields,
				"batch_no": row.batch_no,
				# "set_basic_rate_manually": 1,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
			})

		se.save()
		se.submit()


#***************************cancel doc***************************************
	def cancel_stock_entry(self):

		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"custom_reference_doc": self.doctype,
				"custom_reference_id": self.name,
				"docstatus": 1
			},
			pluck="name"
		)

		for name in stock_entries:
			se = frappe.get_doc("Stock Entry", name)
			se.flags.ignore_links = True
			se.cancel()


#****************************delete doc**********************************

	def delete_stock_entry(self):
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"custom_reference_doc": self.doctype,
				"custom_reference_id": self.name,
			},
			pluck="name"
		)

		for name in stock_entries:
			doc = frappe.get_doc("Stock Entry", name)

			if doc.docstatus == 1:
				doc.cancel()

			doc.delete(ignore_permissions=True)

