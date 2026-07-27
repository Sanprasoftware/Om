# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt


class Maintenance(Document):
	def on_submit(self):
		self.create_stock_entry()
	
	def before_save(self):
		self.calculate_qty_amount()

	def on_cancel(self):
		self.cancel_stock_entry()

	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "Maintenance"
		se.custom_reference_doc = self.doctype
		se.custom_reference_id = self.name
		se.flags.maintenance_basic_rates = [flt(row.basic_rate) for row in self.items]
		for operator_row in self.operator_name:
			se.append("custom_operator_name", {
				"operator_name": operator_row.operator_name,
			})
		se.custom_machine_name = self.machine_name
		se.custom_shift = ""
		se.custom_batch_no = ""
		se.set_posting_time = 1
		se.posting_date = self.issue_date
		se.remarks = f"Created from Maintenance {self.name}"

		for row in self.items:
			se.append("items", {
				"item_code": row.item,
				"set_basic_rate_manually": 1,
				"allow_zero_valuation_rate": 1,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				# "t_warehouse": row.target_warehouse,
				"uom": row.uom,
				"batch_no": row.batch_no,
				"basic_rate": row.basic_rate,
			})

		se.insert(ignore_permissions=True)
		preserve_maintenance_basic_rates(se)
		se.flags.ignore_validate = True
		se.submit()


	def cancel_stock_entry(self):
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "Maintenance",
				"remarks": f"Created from Maintenance {self.name}",
				"docstatus": 1,
			},
			pluck="name"
		)

		for name in stock_entries:
			frappe.get_doc("Stock Entry", name).cancel()


	def calculate_qty_amount(self):
		if self.items:
			total_qty = 0
			total_amount = 0
			for row in self.items:
				row.basic_amount = flt(row.qty) * flt(row.basic_rate)
				total_qty += flt(row.qty)
				total_amount += row.basic_amount
			self.total_qty = total_qty
			self.total_amount = total_amount
	
	@frappe.whitelist()
	def set_rate(self):

		for row in self.items:

			if row.item and row.source_warehouse:

				rate, act_qty = frappe.db.get_value(
					"Bin",
					{
						"item_code": row.item,
						"warehouse": row.source_warehouse
					},
					["valuation_rate", "actual_qty"]
				) or (0, 0)

				row.basic_rate = rate or 0
				row.actual_qty = act_qty or 0
    
#**********************************************************************************
	def on_trash(self):
		self.delete_stock_entry()
	
	def delete_stock_entry(self):
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "Maintenance",
				"remarks": f"Created from Maintenance {self.name}",
			},
			pluck="name"
		)

		for name in stock_entries:
			doc = frappe.get_doc("Stock Entry", name)

			if doc.docstatus == 1:
				doc.cancel()

			doc.delete(ignore_permissions=True)
    


def preserve_maintenance_basic_rates(doc, method=None):
	"""Keep Maintenance rates after ERPNext calculates outgoing stock rates."""
	basic_rates = doc.flags.get("maintenance_basic_rates")
	if basic_rates is None:
		return

	if len(basic_rates) != len(doc.items):
		frappe.throw("Could not apply Maintenance rates to Stock Entry items.")

	for row, basic_rate in zip(doc.items, basic_rates):
		row.set_basic_rate_manually = 1
		row.basic_rate = flt(basic_rate)

	doc.calculate_rate_and_amount(reset_outgoing_rate=False)




