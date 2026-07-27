# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document


class Reprocess(Document):

	def on_submit(self):
		self.create_stock_entry()
		self.validate_is_finish_item()
	
	def on_cancel(self):
		self.cancel_stock_entry()

	def _get_stock_uom(self, item_code):
		if not item_code:
			return None
		return frappe.db.get_value("Item", item_code, "stock_uom")

	def validate_is_finish_item(self):
		if not any(row.is_finished_item for row in self.item):
			frappe.throw("Please mark at least one item as Finished Item in the Item table")

	# @frappe.whitelist()
	# def add_item_data(self):
	# 	self.set("item", [])

	# 	total_raw = sum(flt(row.qty) for row in self.get("scrap_item") or [])
	# 	total_wst = sum(flt(row.qty) for row in self.get("wastage") or [])
	# 	total_fg  = sum(flt(row.qty) for row in self.get("fg_item") or [])
		
	# 	if total_fg <= 0:
	# 		frappe.throw("FG Qty must be greater than 0")
	# 	net_qty = total_raw - total_wst
	# 	if net_qty <= 0:
	# 		frappe.throw("Net Qty must be greater than 0")
	# 	per_fg_qty = net_qty / total_fg 

		# for row in self.get("scrap_item") or []:
		# 	if not (row.item_code and row.qty):
		# 		continue
		# 	self.append("item", {
		# 		"item_code": row.item_code,
		# 		"qty": flt(row.qty),
		# 		"source_warehouse": row.warehouse,
		# 		"batch_no": row.batch,
		# 		"uom": self._get_stock_uom(row.item_code),
		# 		"is_finished_item": 0,
		# 		"is_scrap_item": 0
		# 	})

		# for fg in self.get("fg_item") or []:
		# 	if not (fg.item_code and fg.qty):
		# 		continue
		# 	for i in range(int(flt(fg.qty))):
		# 		self.append("item", {
		# 			"item_code": fg.item_code,
		# 			"qty": per_fg_qty,   # ✅ CALCULATED VALUE
		# 			"target_warehouse": fg.warehouse,
		# 			"batch_no": fg.batch if fg.batch else None,
		# 			"uom": self._get_stock_uom(fg.item_code),
		# 			"is_finished_item": 1,
		# 			"is_scrap_item": 0
		# 		})

		# for ws in self.get("wastage") or []:
		# 	if not (ws.item_code and ws.qty):
		# 		continue
		# 	self.append("item", {
		# 		"item_code": ws.item_code,
		# 		"qty": flt(ws.qty),
		# 		"target_warehouse": ws.warehouse,
		# 		"batch_no": ws.batch if ws.batch else None,
		# 		"uom": self._get_stock_uom(ws.item_code),
		# 		"is_finished_item": 0,
		# 		"is_scrap_item": 1
		# 	})

		# return self

	@frappe.whitelist()
	def calculate_amount(self):
		for row in self.get("item") or []:
			if row.item_code and row.qty:				
				row.basic_amount = flt(row.qty) * flt(row.basic_rate_as_per_stock_uom)
			else:
				row.basic_amount = 0
	


	def create_stock_entry(self):

		se = frappe.new_doc("Stock Entry")

		se.stock_entry_type = self.stock_entry_type
		se.custom_shift = self.shift

		# OPTIONAL:
		# If custom_operator_names is a Text/Data field
		# then convert operators into comma-separated string

		operator_list = []

		for op in self.operator_names:
			operator_name = frappe.db.get_value(
				"Employee",
				op.operator_name,
				"employee_name"
			) or op.operator_name

			operator_list.append(operator_name)

		se.custom_operator_names = ", ".join(operator_list)

		# LINK REPROCESS DOC
		# se.custom_reprocess_reference = self.name

		for row in self.item:

			se.append("items", {
				"item_code": row.item_code,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"uom": row.uom,
				"batch_no": row.batch_no,
				"basic_rate": row.basic_rate_as_per_stock_uom,
				"is_finished_item": row.is_finished_item,  
				"is_scrap_item": row.is_scrap_item,
				
			})

		se.insert(ignore_permissions=True)
		se.submit()


	def cancel_stock_entry(self):

		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"custom_reprocess_reference": self.name,
				"docstatus": 1
			},
			pluck="name"
		)

		for name in stock_entries:

			se = frappe.get_doc("Stock Entry", name)

			if se.docstatus == 1:
				se.cancel()
