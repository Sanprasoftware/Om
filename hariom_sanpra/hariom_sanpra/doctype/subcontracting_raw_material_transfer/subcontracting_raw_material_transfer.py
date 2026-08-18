# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class SubcontractingRawMaterialTransfer(Document):
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
		se.posting_date = self.posting_date
		se.posting_time = self.posting_time
		se.custom_reference_doc = self.doctype
		se.custom_reference_id = self.name
		se.flags.subcontracting_transfer_basic_rates = [flt(row.rate) for row in self.items]
		for operator in self.operator_name:
			se.append("custom_operator_name", {
				"operator_name": operator.operator_name,
			})
		for row in self.items:
			se.append("items", {
				"item_code": row.item_code,
				"set_basic_rate_manually": 1,
				"allow_zero_valuation_rate": 1,
				"qty": row.qty,
				"uom": row.uom,
				"basic_rate": row.rate,
				"use_serial_batch_fields":row.use_serial_batch_fields,
				"batch_no": row.batch_no,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,

			})

		se.save()
		preserve_subcontracting_transfer_basic_rates(se)
		se.flags.ignore_validate = True
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



def preserve_subcontracting_transfer_basic_rates(stock_entry):
	"""Keep the transfer rates after Stock Entry calculates outgoing valuation rates."""
	basic_rates = stock_entry.flags.get("subcontracting_transfer_basic_rates")
	if basic_rates is None:
		return

	if len(basic_rates) != len(stock_entry.items):
		frappe.throw(
			"Could not apply Subcontracting Raw Material Transfer rates to Stock Entry items."
		)

	for row, basic_rate in zip(stock_entry.items, basic_rates):
		row.set_basic_rate_manually = 1
		row.basic_rate = flt(basic_rate)

	stock_entry.calculate_rate_and_amount(reset_outgoing_rate=False)
