// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Assigned for Quality Inspection Report"] = {
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
			fieldname: "quality_person",
			label: __("Quality Person"),
			fieldtype: "Link",
			options: "User"
		}
	],
};
