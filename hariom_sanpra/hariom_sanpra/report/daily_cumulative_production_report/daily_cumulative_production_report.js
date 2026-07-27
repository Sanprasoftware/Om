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
			fieldname: "machine_name",
			label: __("Machine Name"),
			fieldtype: "Link",
			options: "Machine Name",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
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
	formatter(value, row, column, data, default_formatter) {
		const formatted_value = default_formatter(value, row, column, data);
		if (!data?.is_total_row) return formatted_value;

		const color = AVERAGE_FIELDS.has(column.fieldname) ? "blue" : "inherit";
		return `<span style="font-weight: 700; color: ${color}">${formatted_value}</span>`;
	},
};

const AVERAGE_FIELDS = new Set([
	"mc_run",
	"prod_percent",
	"d_time_percent",
	"wastage_percent",
	"ld_percent",
	"trim_percent",
	"other_percent",
	"std_gsm",
	"act_gsm",
]);
