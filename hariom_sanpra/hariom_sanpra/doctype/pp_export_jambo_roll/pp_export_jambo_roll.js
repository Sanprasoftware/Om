// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("PP EXport Jambo Roll", {
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

		add_stock_ledger_button(frm);
		
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
		// frm.fields_dict["wastage"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
		// 	let row = locals[cdt][cdn];

		// 	return {
		// 		filters: {
		// 			item: row.item
		// 		}
		// 	};
		// };
	},
});

function add_stock_ledger_button(frm) {
	if (frm.doc.docstatus !== 1) return;

	frappe.db
		.get_value(
			"Stock Entry",
			{ custom_reference_id: frm.doc.name },
			"name"
		)
		.then((r) => {
			if (!r.message || !r.message.name) {
				console.log(r.message)
				frappe.msgprint(__("Stock Entry not found."));
				return;
			}

			frm.add_custom_button(
				__("Stock Ledger"),
				function () {
					frappe.route_options = {
						company: frappe.defaults.get_user_default("Company"),
						voucher_no: r.message.name,
						from_date: frm.doc.date,
						to_date: frm.doc.date,
					};

					frappe.set_route("query-report", "Stock Ledger Hariom");
				},
				__("View")
			);
		});
}