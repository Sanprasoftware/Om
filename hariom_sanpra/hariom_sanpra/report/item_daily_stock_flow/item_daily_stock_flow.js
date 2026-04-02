// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Item Daily Stock Flow"] = {
	filters: [
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			label: __("Date"),
			fieldname: "date",
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			label: __("Item"),
			fieldname: "item_code",
			fieldtype: "Link",
			options: "Item",
		},
		{
			label: __("Warehouse"),
			fieldname: "warehouse",
			fieldtype: "Link",
			options: "Warehouse",
			default: "Stores - OM",
		},
	],
};
