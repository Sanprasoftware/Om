# Copyright (c) 2026, Sanpra Software Solution and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import flt
from frappe.model.document import Document

class GDRewinding(Document):
	def _get_stock_uom(self, item_code):
		if not item_code:
			return None
		return frappe.db.get_value("Item", item_code, "stock_uom")
	
	@frappe.whitelist()
	def add_items(self):
		self.set("items", [])
		total_raw = sum(flt(row.qty) for row in self.get("raw_items") or [])
		total_wst = sum(flt(row.qty) for row in self.get("wastage_items") or [])
		total_fg  = sum(flt(row.qty) for row in self.get("fg_items") or [])
		if total_fg <= 0:
			frappe.throw("FG Qty must be greater than 0")
		net_qty = total_raw - total_wst
		if net_qty <= 0:
			frappe.throw("Net Qty must be greater than 0")
		per_fg_qty = net_qty / total_fg 

		for row in self.get("raw_items") or []:
			if not (row.item_code and row.qty):
				continue
			self.append("items", {
				"item_code": row.item_code,
				"qty": flt(row.qty),
				"source_warehouse": row.warehouse,
				"gsm" : row.gsm,
				"grade" : row.grade,
				"roll_qty" : row.roll_qty,
				"batch": row.batch,
				"uom": self._get_stock_uom(row.item_code),
				"is_finished_item": 0,
				"is_scrap_item": 0
			})

		for fg in self.get("fg_items") or []:
			if not (fg.item_code and fg.qty):
				continue
			for i in range(int(flt(fg.qty))):
				self.append("items", {
					"item_code": fg.item_code,
					"qty": per_fg_qty,   # ✅ CALCULATED VALUE
					"target_warehouse": fg.warehouse,
					"batch": fg.batch,
					"batch_no": row.batch if row.batch else None,
					"uom": self._get_stock_uom(fg.item_code),
					"is_finished_item": 1,
					"is_scrap_item": 0
				})

		for ws in self.get("wastage_items") or []:
			if not (ws.item_code and ws.qty):
				continue
			self.append("items", {
				"item_code": ws.item_code,
				"qty": flt(ws.qty),
				"target_warehouse": ws.warehouse,
				"batch": ws.batch,
				"batch_no": row.batch if row.batch else None,
				"uom": self._get_stock_uom(ws.item_code),
				"is_finished_item": 0,
				"is_scrap_item": 1
			})

		return self

	def before_save(self):
		self.cal_net_weight()

	def cal_net_weight(self):
		for row in self.items:
			if row.source_warehouse:
				continue
			row.net_weight = row.gross_weight - row.core_weight
			row.roll_sqr_meter = (row.roll_actual_size / 39.37) * row.roll_meter
			if row.roll_sqr_meter:
				row.roll_actual_gsm = (row.net_weight / row.roll_sqr_meter) * 1000
			else:
				row.roll_actual_gsm = 0
#*********************************************************				
	def on_submit(self):
		self.create_stock_entry()

	def on_cancel(self):
		self.cancel_stock_entry()


	def create_stock_entry(self):
		se = frappe.new_doc("Stock Entry")
		se.stock_entry_type = "GD Rewinding"
		se.custom_operator_name = self.operator_name
		se.custom_machine_name = self.machine_name
		se.custom_shift = self.shift
		se.custom_batch_no = self.batch
		se.custom_tag_in = self.tag_in
		se.custom_tag_out = self.tag_out
		for row in self.items:
			se.append("items", {
				"item_code": row.item_code,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"uom": row.uom,
				"batch_no": row.batch,
				"basic_rate":row.basic_rate
			})

		se.insert(ignore_permissions=True)
		se.submit()


	def cancel_stock_entry(self):
		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"stock_entry_type": "GD Rewinding",
				"docstatus": 1
			},
			pluck="name"
		)

		for name in stock_entries:
			frappe.get_doc("Stock Entry", name).cancel()
