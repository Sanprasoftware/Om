// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Quality Inspection Custom"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			width: 100
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			width: 100
		},
		{
			fieldname: "inspection_type",
			label: __("Inspection Type"),
			fieldtype: "Select",
			options: "\nIncoming\nOutgoing\nIn Process",
			width: 120
		},
		{
			fieldname: "reference_type",
			label: __("Reference Type"),
			fieldtype: "Link",
			options: "DocType",
			width: 150
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: "\nAccepted\nRejected\nCancelled\nHold\nRelease",
			width: 120
		},
		{
			fieldname: "quality_inspection_template",
			label: __("Quality Inspection Template"),
			fieldtype: "Link",
			options: "Quality Inspection Template",
			width: 220
		},
		{
			fieldname: "qi_id",
			label: __("Quality Inspection ID"),
			fieldtype: "Link",
			options: "Quality Inspection",
			width: 220
		},
		{
			fieldname: "party_type",
			label: __("Party Type"),
			fieldtype: "Select",
			options: "\nSupplier\nCustomer",
			on_change: function(report) {
				report.set_filter_value("party", "");
			},
		},
		{
			fieldname: "party",
			label: __("Party"),
			fieldtype: "Dynamic Link",
			options: "party_type",
			get_options() {
				return frappe.query_report.get_filter_value("party_type");
			}
		},
		{
			fieldname: "parameter",
			label: __("Parameter"),
			fieldtype: "Link",
			options: "Quality Inspection Parameter",
			width: 220
		},
	],
};
