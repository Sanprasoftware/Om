// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Maintenance Issue Slip Report"] = {
	filters: [
		{
			fieldname: "id",
			label: __("ID"),
			fieldtype: "Link",
			options: "Maintenance",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
		},
		{
			fieldname: "maintains_oper",
			label: __("Maintenance Oper."),
			fieldtype: "Select",
			options: ["", "General Maintains", "Preventive Maintains", "R&D", "Breakdown", "KCR", "Other"],
		},
		{
			fieldname: "machine_name",
			label: __("Machine Name"),
			fieldtype: "Link",
			options: "Machine Name",
		},
		{
			fieldname: "operator_name",
			label: __("Operator Name"),
			fieldtype: "Link",
			options: "Employee",
		},
	],
};
