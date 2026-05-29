// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Delivery Challan"] = {
	filters: [
		{
			label: __("From Date"),
			fieldname: "from_date",
			fieldtype: "Date",
		},
		{
			label: __("To Date"),
			fieldname: "to_date",
			fieldtype: "Date",
		},
		{
			label: __("Id"),
			fieldname: "delivery_challan",
			fieldtype: "Link",
			options: "delivery challan",
		},
	],
};
