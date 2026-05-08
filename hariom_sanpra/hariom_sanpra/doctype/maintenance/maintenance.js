// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance", {
	refresh(frm) {
		frm.fields_dict["items"].grid.get_field("batch_no").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item
				}
			};
		}; 
    },
});


frappe.ui.form.on("Maintenance Items", {
	item(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.call({
			method: "set_rate",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("items");
			}
		})
	},
	source_warehouse(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.call({
			method: "set_rate",
			doc: frm.doc,
			callback: function(r) {
				refresh_field("items");
			}
		})
	}
});