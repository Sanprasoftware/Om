// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Daily-Cumulative Production Report"] = {
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
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "report_based_on",
			label: __("Report Based On"),
			fieldtype: "Select",
			options: "\nItem Wise\nEntry Wise",
			default: "Item Wise",
		},
		{
			fieldname: "id",
			label: __("Id"),
			fieldtype: "Link",
			options: "Stock Entry",
			depends_on: "eval:doc.report_based_on == 'Entry Wise'",
		},
		{
			fieldname: "manufacturing_type",
			label: __("Manufacturing Type"),
			fieldtype: "Select",
			options: "\nPONDLINE\nPIPE\nPP EXPORT",
		},
	],
};
 
