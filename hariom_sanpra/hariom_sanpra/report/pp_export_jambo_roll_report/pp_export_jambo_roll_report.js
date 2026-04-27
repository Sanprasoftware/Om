// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["PP EXport Jambo Roll Report"] = {
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
			options: "Joint Machine",
		},
		{
			fieldname: "operator_name",
			label: __("Operator Name"),
			fieldtype: "Link",
			options: "Employee",
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
	formatter(value, row, column, data, default_formatter) {
		const formatted = default_formatter(value, row, column, data);
		if (!data) return formatted;

			if (column.fieldname === "item_code" || column.fieldname === "item_name") {
				if (data.item_type === "Scrap") {
					return `<span style="color: #1e40af; font-weight: 600;">${formatted}</span>`;
				}
			if (data.item_type === "Finished") {
				return `<span style="color: #1a7f37; font-weight: 600;">${formatted}</span>`;
			}
			if (data.item_type === "Raw") {
				return `<span style="color: #c62828; font-weight: 600;">${formatted}</span>`;
			}
		}

		return formatted;
	},
};
 