// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Production Report"] = {
	filters: [
		// {
		// 	fieldname: "from_date",
		// 	label: __("From"),
		// 	fieldtype: "Date",
		// 	default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		// 	reqd: 1,
		// 	width: "100px",
		// },
		// {
		// 	fieldname: "to_date",
		// 	label: __("To"),
		// 	fieldtype: "Date",
		// 	default: frappe.datetime.get_today(),
		// 	reqd: 1,
		// 	width: "100px",
		// },
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
			options: "Stock Entry",
		},
		{
			fieldname: "operator_name",
			label: __("Operator Name"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "mc_name",
			label: __("Machine Name"),
			fieldtype: "Link",
			options: "Machine Name",
		},
		{
			fieldname: "custom_shift",
			label: __("Shift"),
			fieldtype: "Link",
			options: "Shift",
		},
		{
			fieldname: "batch_no",
			label: __("Batch No"),
			fieldtype: "Link", 
			options: "Batch No"
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
	],
};
