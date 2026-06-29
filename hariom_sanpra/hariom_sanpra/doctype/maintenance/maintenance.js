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
		// Fetch actual qty and rate for old records
		if (!frm.is_new()) {
			update_rate_qty(frm);
		}
    },
});


frappe.ui.form.on("Maintenance Items", {
	qty: function(frm, cdt, cdn) {
		calculate_amount(cdt, cdn);
	},

	basic_rate: function(frm, cdt, cdn) {
		calculate_amount(cdt, cdn);
	},
	item(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		frappe.call({
			method: "set_rate",
			doc: frm.doc,
			callback: function(r) {
				console.log(frm.doc.items);
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
function calculate_amount(cdt, cdn) {
	let row = locals[cdt][cdn];
	frappe.model.set_value(cdt,cdn,"basic_amount",flt(row.qty) * flt(row.basic_rate));
}

function update_rate_qty(frm) {

	frappe.call({
		method: "set_rate",
		doc: frm.doc,

		callback: function(r) {

			console.log(frm.doc.items);

			frm.refresh_field("items");
		}
	});
}