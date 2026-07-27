# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class RKSlittingMachine(Document):
	def _get_stock_uom(self, item):
		if not item:
			return None
		return frappe.db.get_value("Item", item, "stock_uom")

	@frappe.whitelist()
	def add_items(self):
		self.set("items", [])
		total_raw = sum(flt(row.qty) for row in self.get("raw_items") or [])
		total_wst = sum(flt(row.qty) for row in self.get("wastage_items") or [])
		total_fg  = sum(flt(row.qty) for row in self.get("fg_item") or [])
		if total_fg <= 0:
			frappe.throw("FG Qty must be greater than 0")
		net_qty = total_raw - total_wst
		if net_qty <= 0:
			frappe.throw("Net Qty must be greater than 0")
		per_fg_qty = net_qty / total_fg 

		for row in self.get("raw_items") or []:
			if not (row.item and row.qty):
				continue
			self.append("items", {
				"item": row.item,
				"qty": flt(row.qty),
				"source_warehouse": row.warehouse,
				# "gsm" : row.gsm,
				# "grade" : row.grade,
				# "roll_qty" : row.roll_qty,
				"batch_no": row.batch,
				"uom": self._get_stock_uom(row.item),
				"is_finished_item": 0,
				"is_scrap_item": 0
			})

		for fg in self.get("fg_item") or []:
			if not (fg.item and fg.qty):
				continue
			for i in range(int(flt(fg.qty))):
				self.append("items", {
					"item": fg.item,
					"qty": per_fg_qty,   # ✅ CALCULATED VALUE
					"target_warehouse": fg.warehouse,
					"batch": fg.batch,
					"batch_no": fg.batch if fg.batch else None,
					"uom": self._get_stock_uom(fg.item),
					"is_finished_item": 1,
					"is_scrap_item": 0
				})

		for ws in self.get("wastage_items") or []:
			if not (ws.item and ws.qty):
				continue
			self.append("items", {
				"item": ws.item,
				"qty": flt(ws.qty),
				"target_warehouse": ws.warehouse,
				"batch": ws.batch,
				"batch_no": ws.batch if ws.batch else None,
				"uom": self._get_stock_uom(ws.item),
				"is_finished_item": 0,
				"is_scrap_item": 1
			})

		return self

	
#************************************************************************		
	def on_submit(self):
		self.create_stock_entry()

	def on_cancel(self):
		self.cancel_stock_entry()


	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "RK - PIPE"
		se.custom_operator_name = self.operator_name
		se.custom_machine_name = self.machine_name
		se.custom_shift = self.shift
		se.custom_batch_no = self.batch
		# se.custom_tag_in = self.tag_in
		# se.custom_tag_out = self.tag_out
		for row in self.items:
			se.append("items", {
				"item_code": row.item,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"uom": row.uom,
				"batch_no": row.batch_no,
				"is_finished_item": row.is_finished_item,  
				"is_scrap_item": row.is_scrap_item,
			})

		se.insert(ignore_permissions=True)
		se.submit()

	def cancel_stock_entry(self):
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "RK - PIPE",
				"docstatus": 1
			},
			pluck="name"
		)

		for name in stock_entries:
			frappe.get_doc("Stock Entry", name).cancel()


	