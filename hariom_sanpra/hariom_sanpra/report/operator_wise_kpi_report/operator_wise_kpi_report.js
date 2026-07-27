// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.query_reports["Operator Wise KPI Report"] = {
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
			options: "Operator Name",
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
			options: "\nPONDLINE\nPIPE\nPP EXPORT",
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
			if (column.fieldname === "variation_percentage") {
				if (data.variation_percentage > 0) {
					return `<span style="color: red; font-weight: bold;">${formatted}</span>`;
				}
			}
		return formatted;
	},

	after_datatable_render(datatable) {
		if (!datatable.options.showTotalRow || datatable.__average_row_enabled) {
			return;
		}

		datatable.__average_row_enabled = true;
		const render_standard_footer = datatable.bodyRenderer.renderFooter.bind(
			datatable.bodyRenderer
		);

		datatable.bodyRenderer.renderFooter = function () {
			render_standard_footer();

			const rows = this.visibleRows || [];
			if (!rows.length) return;

			const columns = this.datamanager.getColumns();
			const first_data_column = this.datamanager.getStandardColumnCount();
			const average_row = columns.map((column, index) => {
				let content = "";
				let cell_column = column;

				if (index === first_data_column) {
					content = __("Average");
					cell_column = { ...column, fieldtype: "Data" };
				} else if (frappe.model.is_numeric_field(column.fieldtype)) {
					const values = rows
						.map((row) => row[index]?.content)
						.filter(
							(value) =>
								value !== null &&
								value !== undefined &&
								value !== "" &&
								Number.isFinite(Number(value))
						)
						.map(Number);

					if (values.length) {
						content =
							values.reduce((total, value) => total + value, 0) /
							values.length;
					}
				}

				return {
					content,
					isTotalRow: 1,
					colIndex: column.colIndex,
					column: cell_column,
				};
			});

			this.footer.insertAdjacentHTML(
				"beforeend",
				this.rowmanager.getRowHTML(average_row, {
					isTotalRow: 1,
					rowIndex: "averageRow",
				})
			);

			const average_row_element = this.footer.lastElementChild;
			average_row_element.style.fontWeight = "bold";

			average_row.forEach((cell, index) => {
				if (
					cell.content !== "" &&
					frappe.model.is_numeric_field(cell.column.fieldtype)
				) {
					const value_element = average_row_element.children[index]?.querySelector(
						".dt-cell__content"
					);
					if (value_element) value_element.style.color = "#1e40af";
				}
			});
		};

		datatable.bodyRenderer.renderFooter();
	},
};

