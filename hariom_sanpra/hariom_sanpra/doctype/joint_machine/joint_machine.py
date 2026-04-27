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
		self.set("items", [])
		total_raw = sum(flt(row.qty) for row in self.get("raw_item") or [])
		total_wst = sum(flt(row.qty) for row in self.get("wastage_item") or [])
		total_fg  = sum(flt(row.qty) for row in self.get("fg_item") or [])
		if total_fg <= 0:
			frappe.throw("FG Qty must be greater than 0")
		net_qty = total_raw - total_wst
		if net_qty <= 0:
			frappe.throw("Net Qty must be greater than 0")
		per_fg_qty = net_qty / total_fg 

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
				"is_scrap_item": 0
			})

		for fg in self.get("fg_item") or []:
			if not (fg.item_code and fg.qty):
				continue
			gsm = flt(self.raw_item[0].gsm) if self.raw_item else 0
			for i in range(int(flt(fg.qty))):
				self.append("items", {
					"item_code": fg.item_code,
					"qty": per_fg_qty,   # ✅ CALCULATED VALUE
					"target_warehouse": fg.warehouse,
					"batch_no": fg.batch,
					"uom": self._get_stock_uom(fg.item_code),
					"is_finished_item": 1,
					"is_scrap_item": 0,
					"length": fg.length,
					"width": fg.width,
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
				"is_scrap_item": 1
			})

		return self

	def before_save(self):
		self.calculation()

	def calculation(self):
		raw_gsm = flt(self.raw_item[0].gsm) if self.raw_item else 0

		for row in self.items:
			if row.source_warehouse:
				continue

			row.output_weight = (
				flt(row.length) * flt(row.width) * ((raw_gsm / 1000) / 10.758)
			)

			if row.is_finished_item == 1:
				row.qty = row.output_weight