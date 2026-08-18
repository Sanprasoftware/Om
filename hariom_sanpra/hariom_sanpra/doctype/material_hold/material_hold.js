// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Material Hold", {
	refresh(frm) {
        frm.fields_dict["items"].grid.get_field("batch_no").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item_code
				}
			};
		};
	},
});
frappe.ui.form.on("Hold Item Child", {
	qty: calculate_amount,
	basic_rate: calculate_amount,
});

function calculate_amount(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	row.amount = (row.qty || 0) * (row.basic_rate || 0);
	frm.refresh_field("items");
}
