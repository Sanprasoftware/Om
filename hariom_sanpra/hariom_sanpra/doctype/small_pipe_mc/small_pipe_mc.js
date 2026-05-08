// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Small Pipe mc", {
	add_data(frm) {
		frm.call({
			method: "add_items",
			doc: frm.doc,
			callback: function(r) {
				frm.refresh_field("items");
			}
		});
	},
	refresh(frm) {
		frm.fields_dict["items"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item_code
				}
			};
		};
		frm.fields_dict["raw_items"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item
				}
			};
		};
		frm.fields_dict["fg_items"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item
				}
			};
		};
		frm.fields_dict["wastage_items"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item
				}
			};
		};
	},
});

