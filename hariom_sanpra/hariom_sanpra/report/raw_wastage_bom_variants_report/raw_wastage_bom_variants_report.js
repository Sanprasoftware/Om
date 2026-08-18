// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Raw Wastage BOM Variants Report"] = {
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
			options: "Stock Entry",
		},
		{
			fieldname: "operator_name",
			label: __("Operator Name"),
			fieldtype: "Link",
			options: "Employee",
		},
		{
			fieldname: "machine_name",
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
			options: "Batch"
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "report_based_on",
			label: __("Report Based On"),
			fieldtype: "Select",
			options: "\nBOM Wise",
			default: "",
		},
		{
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
		},
		{
			fieldname: "manufacturing_type",
			label: __("Manufacturing Type"),
			fieldtype: "Select",
			options: "\nPONDLINE\nPIPE\nPP EXPORT\nMURGHAS",
		},
		{
			fieldname: "feet",
			label: __("Feet"),
			fieldtype: "Link",
			options: "FEET",
		},
	],

	formatter(value, row, column, data, default_formatter) {
		const formatted = default_formatter(value, row, column, data);
		if (!data) return formatted;

			// if (column.fieldname === "item_code") {
			// 	if (data.item_type === "Scrap") {
			// 		return formatted.replace(
			// 			"<a ",
			// 			'<a style="color:#1e40af;font-weight:600;" '
			// 		);
			// 	}
			// 	if (data.item_type === "Finished") {
			// 		return formatted.replace(
			// 			"<a ",
			// 			'<a style="color:#1a7f37;font-weight:600;" '
			// 		);
			// 	}
			// 	if (data.item_type === "Raw") {
			// 		return formatted.replace(
			// 			"<a ",
			// 			'<a style="color:#c62828;font-weight:600;" '
			// 		);
			// 	}
			// }

			// Item Name (Data field)
			// if (column.fieldname === "item_name") {
			// 	if (data.item_type === "Scrap") {
			// 		return `<span style="color:#1e40af;font-weight:600;">${formatted}</span>`;
			// 	}
			// 	if (data.item_type === "Finished") {
			// 		return `<span style="color:#1a7f37;font-weight:600;">${formatted}</span>`;
			// 	}
			// 	if (data.item_type === "Raw") {
			// 		return `<span style="color:#c62828;font-weight:600;">${formatted}</span>`;
			// 	}
			// }
			if (column.fieldname === "variation_percentage") {
				if (data.variation_percentage > 0) {
					return `<span style="color: red; font-weight: bold;">${formatted}</span>`;
				}
			}
		return formatted;
	},

	after_datatable_render(datatable) {
		if (!datatable.options.showTotalRow || datatable.__variation_total_enabled) {
			return;
		}

		datatable.__variation_total_enabled = true;
		const render_standard_footer = datatable.bodyRenderer.renderFooter.bind(
			datatable.bodyRenderer
		);

		datatable.bodyRenderer.renderFooter = function () {
			render_standard_footer();

			const rows = this.visibleRows || [];
			const columns = this.datamanager.getColumns();
			const get_column_index = (fieldname) =>
				columns.findIndex(
					(column) => column.id === fieldname || column.fieldname === fieldname
				);
			const work_order_index = get_column_index("work_order_qty");
			const variation_index = get_column_index("variation");
			const percentage_index = get_column_index("variation_percentage");

			if (
				!rows.length ||
				work_order_index < 0 ||
				variation_index < 0 ||
				percentage_index < 0
			) {
				return;
			}

			const sum_column = (column_index) =>
				rows.reduce((total, row) => {
					const value = Number(row[column_index]?.content);
					return total + (Number.isFinite(value) ? value : 0);
				}, 0);
			const work_order_total = sum_column(work_order_index);
			const variation_total = sum_column(variation_index);
			const percentage = work_order_total
				? flt((variation_total / work_order_total) * 100, 2)
				: 0;
			const percentage_col_index = columns[percentage_index].colIndex;
			const percentage_cell = this.footer.querySelector(
				".dt-row:last-child .dt-cell--col-" +
					percentage_col_index +
					" .dt-cell__content"
			);

			if (percentage_cell) {
				percentage_cell.innerHTML = frappe.format(percentage, { fieldtype: "Percent" });
			}
		};

		datatable.bodyRenderer.renderFooter();
	},
};

