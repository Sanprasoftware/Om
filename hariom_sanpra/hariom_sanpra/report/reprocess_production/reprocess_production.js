frappe.query_reports["Reprocess Production"] = {
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
			fieldname: "shift",
			label: __("Shift"),
			fieldtype: "Link",
			options: "Shift",
		},

		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},

		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},

		{
			fieldname: "operator",
			label: __("Operator"),
			fieldtype: "Link",
			options: "Employee",
		},

		{
			fieldname: "reprocess_type",
			label: __("Reprocess Type"),
			fieldtype: "Select",
			options: "\nPONDLINE\nPIPE\nPP EXPORT\nMURGHAS",
		},
		{
			fieldname: "mc_name",
			label: __("M/C Name"),
			fieldtype: "Link",
			options: "Stock Entry Type",
			get_query: function () {
				return {
					filters: {
						name: ["in", ["Old RP MC", "RR MC"]]
					}
				};
			}
		}

	],
};