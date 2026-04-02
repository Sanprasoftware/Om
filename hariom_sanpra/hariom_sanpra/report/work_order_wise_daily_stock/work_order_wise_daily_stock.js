// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Work Order Wise Daily Stock"] = {
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
			label: __("Work Order"),
			fieldname: "work_order",
			fieldtype: "Link",
			options: "Work Order",
			reqd: 1,
			get_query: function () {
				return {
					filters: {
						docstatus: 1,
						status: ["in", ["In Process", "Completed", "Stopped"]],
					},
				};
			},
		},
	],
};
