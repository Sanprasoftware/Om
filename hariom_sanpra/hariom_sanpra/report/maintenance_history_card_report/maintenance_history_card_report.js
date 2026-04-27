// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Maintenance History Card Report"] = {
	filters: [
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
			fieldname: "id",
			label: __("Id"),
			fieldtype: "Link",
			options: "Maintenance History Card"
		},
		{
			fieldname: "machine_name",
			label: __("Machine Name"),
			fieldtype: "Link",
			options: "Machine Name",
		},
	],
};
