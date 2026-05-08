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
		se.custom_operator_name = self.operator_name
		se.custom_machine_name = self.machine_name
		se.custom_shift = ""
		se.custom_batch_no = ""
		se.remarks = f"Created from Maintenance {self.name}"

		for row in self.items:
			se.append("items", {
				"item_code": row.item,
				"set_basic_rate_manually": 1,
				"allow_zero_valuation_rate": 1,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"uom": row.uom,
				"batch_no": row.batch_no,
				"basic_rate": row.basic_rate,
			})

		se.insert(ignore_permissions=True)
		# self.set_manual_stock_entry_rates(se)
		# se.flags.ignore_validate = True
		se.submit()

	# def set_manual_stock_entry_rates(self, stock_entry):
	# 	stock_entry.reload()

	# 	for se_item, maintenance_item in zip(stock_entry.items, self.items):
	# 		basic_rate = flt(maintenance_item.basic_rate)
	# 		transfer_qty = flt(se_item.transfer_qty) or flt(se_item.qty)

	# 		se_item.set_basic_rate_manually = 1
	# 		se_item.basic_rate = basic_rate
	# 		se_item.basic_amount = flt(transfer_qty * basic_rate, se_item.precision("basic_amount"))
	# 		se_item.amount = flt(
	# 			se_item.basic_amount
	# 			+ flt(se_item.additional_cost)
	# 			+ flt(se_item.landed_cost_voucher_amount),
	# 			se_item.precision("amount"),
	# 		)
	# 		se_item.valuation_rate = flt(se_item.amount / transfer_qty) if transfer_qty else basic_rate
	# 		se_item.db_update()

	# 	stock_entry.set_total_incoming_outgoing_value()
	# 	stock_entry.set_total_amount()
	# 	stock_entry.db_update()

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
				rate = frappe.db.get_value("Bin", {"item_code": row.item, "warehouse": row.source_warehouse}, "valuation_rate")
				# frappe.throw(str(rate))
				row.basic_rate = rate or 0