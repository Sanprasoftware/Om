# Copyright (c) 2026, Sanpra Software Solution and contributors

import json

import frappe
from frappe import _
from frappe.utils import flt, get_datetime, now_datetime, time_diff_in_seconds
from erpnext.manufacturing.doctype.work_order.work_order import make_stock_entry


class WorkOrderTimeLogMixin:
	def _get_custom_time_logs(self):
		return self.get("custom_job_card_time_log") or []

	def _get_target_qty(self):
		return flt(self.qty)

	def _get_total_completed_qty(self):
		return sum(flt(row.completed_qty) for row in self._get_custom_time_logs())

	def _is_job_fully_completed(self):
		target_qty = self._get_target_qty()
		if target_qty <= 0:
			return False

		return self._get_total_completed_qty() >= target_qty

	def _get_open_time_logs(self):
		return [row for row in self._get_custom_time_logs() if row.from_time and not row.to_time]

	def _get_last_time_log(self):
		time_logs = self._get_custom_time_logs()
		return time_logs[-1] if time_logs else None

	def _get_default_employees(self):
		employees = []
		seen = set()

		for row in self._get_custom_time_logs():
			if row.employee and row.employee not in seen:
				seen.add(row.employee)
				employees.append(row.employee)

		return employees

	def _normalize_employees(self, employees=None):
		if not employees:
			employees = self._get_default_employees()

		if isinstance(employees, str):
			try:
				employees = json.loads(employees)
			except ValueError:
				employees = [employees]

		normalized_employees = []
		for employee in employees or []:
			if isinstance(employee, dict):
				employee = employee.get("employee")

			if employee:
				normalized_employees.append(employee)

		if not normalized_employees:
			frappe.throw(_("Please select at least one employee."))

		return normalized_employees

	def _get_time_log_summary(self):
		time_logs = self._get_custom_time_logs()
		open_time_logs = self._get_open_time_logs()
		is_completed = self._is_job_fully_completed()

		return {
			"has_logs": bool(time_logs),
			"in_progress": bool(open_time_logs),
			"is_paused": bool(time_logs and not open_time_logs and not is_completed),
			"is_completed": is_completed,
			"target_qty": self._get_target_qty(),
			"total_completed_qty": self._get_total_completed_qty(),
			"employees": self._get_default_employees(),
		}

	def _validate_time_tracking_allowed(self):
		if self.docstatus != 1:
			frappe.throw(_("Work Order time tracking is allowed only after submit."))

		if self.status in {"Closed", "Cancelled", "Completed"}:
			frappe.throw(_("You cannot update time logs for a {0} Work Order.").format(self.status))

	def _append_start_logs(self, start_time, employees):
		for employee in employees:
			self.append(
				"custom_job_card_time_log",
				{
					"employee": employee,
					"from_time": start_time,
				},
			)

		if not self.actual_start_date:
			self.actual_start_date = start_time

	def _close_open_logs(self, end_time, completed_qty=0):
		open_time_logs = self._get_open_time_logs()
		if not open_time_logs:
			frappe.throw(_("No active job found for this Work Order."))

		completed_row = None
		for index, row in enumerate(open_time_logs):
			row.to_time = end_time
			row.time_in_mins = flt(time_diff_in_seconds(row.to_time, row.from_time) / 60)
			row.completed_qty = flt(completed_qty) if index == len(open_time_logs) - 1 else 0
			if index == len(open_time_logs) - 1:
				completed_row = row

		return completed_row

	def _save_time_logs(self):
		self.flags.ignore_validate_update_after_submit = True
		self.save()

	def _set_stock_entry_time_log_link(self, stock_entry, time_log_name):
		if not time_log_name:
			return

		stock_entry.custom_job_card_time_log_id = time_log_name

	def _create_draft_manufacture_stock_entry(self, qty, time_log_name=None):
		stock_entry_data = make_stock_entry(self.name, "Manufacture", qty=flt(qty))
		stock_entry = frappe.get_doc(stock_entry_data)
		self._set_stock_entry_time_log_link(stock_entry, time_log_name)
		has_raw_material = any(
			not int(row.get("is_finished_item") or 0) and not int(row.get("is_scrap_item") or 0)
			for row in (stock_entry.get("items") or [])
		)

		if not has_raw_material:
			item_dict = stock_entry.get_bom_raw_materials(flt(qty)) or {}
			for original_item, item in item_dict.items():
				if not item.get("from_warehouse"):
					item["from_warehouse"] = stock_entry.from_warehouse or self.source_warehouse
				item["to_warehouse"] = ""
				if original_item != item.get("item_code"):
					item["original_item"] = original_item

			stock_entry.add_to_stock_entry_detail(item_dict)

		stock_entry.insert()

	def _reconcile_linked_draft_stock_entries(self):
		current_time_log_ids = {row.name for row in self._get_custom_time_logs() if row.name}
		try:
			linked_stock_entries = frappe.get_all(
				"Stock Entry",
				filters={
					"work_order": self.name,
					"purpose": "Manufacture",
					"docstatus": 0,
				},
				fields=["name", "custom_job_card_time_log_id"],
				limit_page_length=0,
			)
		except Exception:
			# custom_job_card_time_log_id field not present on Stock Entry
			return

		for stock_entry in linked_stock_entries:
			link_id = stock_entry.get("custom_job_card_time_log_id")
			if link_id and link_id not in current_time_log_ids:
				frappe.delete_doc("Stock Entry", stock_entry.name, ignore_permissions=True, force=1)

	def _capture_deleted_time_log_row_names(self):
		self.flags.deleted_time_log_row_names = []
		previous_doc = self.get_doc_before_save()
		if not previous_doc:
			return

		previous_row_names = {
			row.name for row in (previous_doc.get("custom_job_card_time_log") or []) if row.name
		}
		current_row_names = {row.name for row in self._get_custom_time_logs() if row.name}
		self.flags.deleted_time_log_row_names = list(previous_row_names - current_row_names)

	def _delete_stock_entries_for_deleted_rows(self):
		deleted_row_names = self.flags.deleted_time_log_row_names or []
		if not deleted_row_names:
			return

		stock_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"work_order": self.name,
				"purpose": "Manufacture",
				"docstatus": 0,
				"custom_job_card_time_log_id": ("in", deleted_row_names),
			},
			pluck="name",
		)
		for stock_entry_name in stock_entries:
			frappe.delete_doc("Stock Entry", stock_entry_name, ignore_permissions=True, force=1)

	def _validate_no_submitted_stock_entry_for_deleted_rows(self):
		deleted_row_names = self.flags.deleted_time_log_row_names or []
		if not deleted_row_names:
			return

		submitted_entries = frappe.get_all(
			"Stock Entry",
			filters={
				"work_order": self.name,
				"purpose": "Manufacture",
				"docstatus": 1,
				"custom_job_card_time_log_id": ("in", deleted_row_names),
			},
			pluck="name",
		)
		if submitted_entries:
			frappe.throw(
				_(
					"Cannot delete Job Time Log row because linked Manufacturing Stock Entry is submitted: {0}"
				).format(", ".join(submitted_entries))
			)

	def before_save(self):
		parent_before_save = getattr(super(), "before_save", None)
		if callable(parent_before_save):
			parent_before_save()
		self._capture_deleted_time_log_row_names()
		self._validate_no_submitted_stock_entry_for_deleted_rows()

	def before_update_after_submit(self):
		parent_before_update_after_submit = getattr(super(), "before_update_after_submit", None)
		if callable(parent_before_update_after_submit):
			parent_before_update_after_submit()
		self._capture_deleted_time_log_row_names()
		self._validate_no_submitted_stock_entry_for_deleted_rows()

	def on_update(self):
		parent_on_update = getattr(super(), "on_update", None)
		if callable(parent_on_update):
			parent_on_update()
		self._delete_stock_entries_for_deleted_rows()
		self._reconcile_linked_draft_stock_entries()

	def on_update_after_submit(self):
		parent_on_update_after_submit = getattr(super(), "on_update_after_submit", None)
		if callable(parent_on_update_after_submit):
			parent_on_update_after_submit()
		self._delete_stock_entries_for_deleted_rows()
		self._reconcile_linked_draft_stock_entries()

	@frappe.whitelist()
	def get_job_log_summary(self):
		return self._get_time_log_summary()

	@frappe.whitelist()
	def start_job(self, start_time=None, employees=None):
		self._validate_time_tracking_allowed()

		if self._get_open_time_logs():
			frappe.throw(_("Job already started for this Work Order."))

		summary = self._get_time_log_summary()
		if summary["is_completed"]:
			frappe.throw(_("Job already completed for this Work Order."))

		start_time = get_datetime(start_time) if start_time else now_datetime()
		employees = self._normalize_employees(employees)

		self._append_start_logs(start_time, employees)
		self._save_time_logs()

	@frappe.whitelist()
	def pause_job(self, end_time=None):
		self._validate_time_tracking_allowed()
		end_time = get_datetime(end_time) if end_time else now_datetime()

		self._close_open_logs(end_time)
		self._save_time_logs()

	@frappe.whitelist()
	def resume_job(self, start_time=None, employees=None):
		self._validate_time_tracking_allowed()

		if self._get_open_time_logs():
			frappe.throw(_("Job is already in progress for this Work Order."))

		summary = self._get_time_log_summary()
		if summary["is_completed"]:
			frappe.throw(_("Completed jobs cannot be resumed."))

		start_time = get_datetime(start_time) if start_time else now_datetime()
		employees = self._normalize_employees(employees)

		self._append_start_logs(start_time, employees)
		self._save_time_logs()

	@frappe.whitelist()
	def complete_job(self, end_time=None, completed_qty=None):
		self._validate_time_tracking_allowed()
		completed_qty = flt(completed_qty)
		completed_time_log_name = None

		if completed_qty <= 0:
			frappe.throw(_("Completed Qty must be greater than 0."))

		if self._is_job_fully_completed():
			frappe.throw(_("Job already completed for this Work Order."))

		target_qty = self._get_target_qty()
		total_completed_qty = self._get_total_completed_qty()
		remaining_qty = flt(target_qty - total_completed_qty)

		if target_qty > 0 and completed_qty > remaining_qty:
			frappe.throw(_("Completed Qty cannot be greater than remaining Qty ({0}).").format(remaining_qty))

		if self._get_open_time_logs():
			end_time = get_datetime(end_time) if end_time else now_datetime()
			completed_row = self._close_open_logs(end_time, completed_qty=completed_qty)
			completed_time_log_name = completed_row.name if completed_row else None
		else:
			last_time_log = self._get_last_time_log()
			if not last_time_log:
				frappe.throw(_("Start the job before completing it."))

			if flt(last_time_log.completed_qty) > 0:
				frappe.throw(_("Start the job before completing it."))

			if last_time_log.to_time:
				last_time_log.completed_qty = completed_qty
				end_time = last_time_log.to_time
				completed_time_log_name = last_time_log.name

		self.actual_end_date = get_datetime(end_time) if end_time else now_datetime()
		self._save_time_logs()
		if not completed_time_log_name:
			last_time_log = self._get_last_time_log()
			completed_time_log_name = last_time_log.name if last_time_log else None
		self._create_draft_manufacture_stock_entry(completed_qty, time_log_name=completed_time_log_name)
