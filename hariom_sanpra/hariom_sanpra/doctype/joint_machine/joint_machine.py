# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class JointMachine(Document):
	def _get_stock_uom(self, item_code):
		if not item_code:
			return None
		return frappe.db.get_value("Item", item_code, "stock_uom")

	@frappe.whitelist()
	def add_items(self):
		# frappe.throw("hi")
		# existing = {}
		# for row in self.get("items") or []:
		# 	key = (row.item_code, row.batch_no)
		# 	existing[key] = row.use_serial_batch_fields

		self.set("items", [])
		total_raw = sum(flt(row.qty) for row in self.get("raw_item") or [])
		total_wst = sum(flt(row.qty) for row in self.get("wastage_item") or [])
		total_fg  = sum(flt(row.qty) for row in self.get("fg_item") or [])
		if total_fg <= 0:
			frappe.throw("FG Qty must be greater than 0")
		net_qty = total_raw - total_wst
		if net_qty <= 0:
			frappe.throw("Net Qty must be greater than 0")
		# per_fg_qty = net_qty / total_fg 

		for row in self.get("raw_item") or []:
			if not (row.item_code and row.qty):
				continue
			self.append("items", {
				"item_code": row.item_code,
				"qty": flt(row.qty),
				"gsm": row.gsm,
				"source_warehouse": row.warehouse,
				"batch_no": row.batch,
				"uom": self._get_stock_uom(row.item_code),
				"is_finished_item": 0,
				"is_scrap_item": 0,
				# "use_serial_no__batch_fields": existing.get(key, 0)
			})

		for fg in self.get("fg_item") or []:
			if not (fg.item_code and fg.qty):
				continue
			gsm = flt(self.raw_item[0].gsm) if self.raw_item else 0
			for i in range(int(flt(fg.qty))):
				self.append("items", {
					"item_code": fg.item_code,
					"qty": fg.qty,   # ✅ CALCULATED VALUE
					"target_warehouse": fg.warehouse,
					"batch_no": fg.batch,
					"uom": self._get_stock_uom(fg.item_code),
					"is_finished_item": 1,
					"is_scrap_item": 0,
					"length": fg.length,
					"width": fg.width,
					# "use_serial_no__batch_fields": existing.get(key, 0)
				})

		for ws in self.get("wastage_item") or []:
			if not (ws.item_code and ws.qty):
				continue
			self.append("items", {
				"item_code": ws.item_code,
				"qty": flt(ws.qty),
				"target_warehouse": ws.warehouse,
				"batch_no": ws.batch,
				"uom": self._get_stock_uom(ws.item_code),
				"is_finished_item": 0,
				"is_scrap_item": 1,
				# "use_serial_no__batch_fields": existing.get(key, 0) 
			})
	
		return self

	def before_save(self):
		# self.add_items()
		self.calculation()

	def calculation(self):
		raw_gsm = flt(self.raw_item[0].gsm) if self.raw_item else 0

		for row in self.items:
			if not row.is_finished_item:
				continue

			row.output_weight = (
				flt(row.length) *
				flt(row.width) *
				((raw_gsm / 1000) / 10.758)
			)

			row.qty = row.output_weight
	
#*********************************************************				
	def on_submit(self):
		# pass
		self.create_stock_entry()

	def on_cancel(self):
		self.cancel_stock_entry()


	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "JOINT M/C"
		se.custom_operator_name = self.operator_name
		se.custom_machine_name = self.machine_name
		se.custom_shift = self.shift
		se.custom_batch_no = self.batch
		# se.custom_tag_in = self.tag_in
		se.custom_tag_out = self.tag_out
		for row in self.items:
			se.append("items", {
				"custom_____stock_entry_type": self.stock_entry_type,
				"item_code": row.item_code,
				"qty": row.qty,
				"uom": row.uom,
				"batch_no": row.batch_no,
				"set_basic_rate_manually": 1,

				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"custom_size_1": row.length,
				"custom_size_2": row.width,
				
			})

		# se.insert(ignore_permissions=True)
		se.save()
		se.submit()


	def cancel_stock_entry(self):
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "JOINT M/C",
				"docstatus": 1
			},
			pluck="name"
		)

		for name in stock_entries:
			frappe.get_doc("Stock Entry", name).cancel()