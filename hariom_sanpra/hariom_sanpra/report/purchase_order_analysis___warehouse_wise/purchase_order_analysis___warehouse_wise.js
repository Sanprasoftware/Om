frappe.query_reports["Purchase Order Analysis - Warehouse Wise"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			reqd: 1,
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			on_change: (report) => {
				report.set_filter_value("name", []);
				report.refresh();
			},
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			reqd: 1,
			default: frappe.datetime.get_today(),
			on_change: (report) => {
				report.set_filter_value("name", []);
				report.refresh();
			},
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "name",
			label: __("Purchase Order"),
			fieldtype: "MultiSelectList",
			options: "Purchase Order",
			get_data: function (txt) {
				const filters = { docstatus: 1 };
				const from_date = frappe.query_report.get_filter_value("from_date");
				const to_date = frappe.query_report.get_filter_value("to_date");

				if (from_date && to_date) {
					filters.transaction_date = ["between", [from_date, to_date]];
				}

				return frappe.db.get_link_options("Purchase Order", txt, filters);
			},
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "MultiSelectList",
			options: ["To Pay", "To Bill", "To Receive", "To Receive and Bill", "Completed", "Closed"],
			get_data: function () {
				return ["To Pay", "To Bill", "To Receive", "To Receive and Bill", "Completed", "Closed"].map(
					(option) => ({ value: option, label: __(option), description: "" })
				);
			},
		},
		{
			fieldname: "group_by_po",
			label: __("Group by Purchase Order"),
			fieldtype: "Check",
			default: 0,
		},
	],

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (["received_qty", "billed_amount"].includes(column.fieldname) && data && data[column.fieldname] > 0) {
			value = `<span style="color:green">${value}</span>`;
		}

		return value;
	},
};
