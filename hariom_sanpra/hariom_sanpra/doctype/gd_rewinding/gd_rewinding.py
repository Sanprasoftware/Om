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
				"batch_no": row.batch,
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
				"batch_no": ws.batch,
				# "batch_no": row.batch if row.batch else None,
				"uom": self._get_stock_uom(ws.item_code),
				"is_finished_item": 0,
				"is_scrap_item": 1
			})
		for row in self.items:
			if row.is_finished_item == 1:
				row.use_serial_no__batch_fields = 0
			else:
				row.use_serial_no__batch_fields = 1
		return self

	def before_save(self):
		for row in self.raw_items:
			if not row.batch:
				frappe.throw(f"Please select Batch for Item {row.item_code}")
		for row in self.wastage_items:
			if not row.batch:
				frappe.throw(f"Please select Batch for Item {row.item_code}")
		for row in self.items:
			if row.use_serial_no__batch_fields == 1 and not row.batch_no:
				frappe.throw(f"Please select Batch for Item {row.item_code}")

		self.cal_net_weight()

	def cal_net_weight(self):
		for row in self.items:
			if row.source_warehouse:
				continue
			row.net_weight = row.gross_weight - row.core_weight
   
			if row.is_finished_item == 1:
				row.qty = row.net_weight

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
		se.set_posting_time = 1
		se.custom_reference_doc = self.doctype
		se.custom_reference_id = self.name
		se.posting_date = self.date
		for operator in self.operator_name:
					se.append("custom_operator_name", {
						"operator_name": operator.operator_name,
					})
		se.custom_machine_name = self.machine_name
		se.custom_shift = self.shift
		se.custom_batch_no = self.batch
		
		for row in self.items:
			se.append("items", {
				"item_code": row.item_code,
				"qty": row.qty,
				"s_warehouse": row.source_warehouse,
				"t_warehouse": row.target_warehouse,
				"uom": row.uom,
				"use_serial_batch_fields" : row.use_serial_no__batch_fields,
				"batch_no": row.batch_no,
				"basic_rate":row.basic_rate,
				"is_finished_item": row.is_finished_item,  
				"is_scrap_item": row.is_scrap_item,
			})

		se.insert(ignore_permissions=True)
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
	def on_trash(self):
		self.delete_stock_entry()

	def delete_stock_entry(self):
		# Remove the reverse link before deleting the linked Stock Entry.
		# Otherwise Frappe blocks deletion because this GD Rewinding still references it.
		if self.stock_entry_id:
			self.db_set("stock_entry_id", None, update_modified=False)

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
