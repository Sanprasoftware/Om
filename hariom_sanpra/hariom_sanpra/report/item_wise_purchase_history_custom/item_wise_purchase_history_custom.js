frappe.query_reports["Item-wise Purchase History Custom"] = {

    filters: [

        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_start()
        },

        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            reqd: 1,
            default: frappe.datetime.month_end()
        },

        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company"
        },

        {
			fieldname: "item_code",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item"
		},

        {
            fieldname: "supplier_group",
            label: __("Supplier Group"),
            fieldtype: "Link",
            options: "Supplier Group"
        },

        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group"
        }
    ]
};