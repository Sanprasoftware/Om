// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Reprocess", {
	add_data(frm) {
        frappe.call({
            method: "add_item_data",
            doc: frm.doc,
            callback: function (r) {
                if (r.message) {
                    console.log(r.message);
                    frm.refresh_field("item");
                }
            },
        })
	},

    refresh(frm) {
		frm.fields_dict["item"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item_code
				}
			};
		};
		frm.fields_dict["scrap_item"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item_code
				}
			};
		};
		frm.fields_dict["fg_item"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item_code
				}
			};
		};
		frm.fields_dict["wastage"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: { 
					item: row.item_code
				}
			};
		};
	},

    setup(frm) {
        frm.set_query("stock_entry_type", function () {
            return {
                filters: [
                    ["Stock Entry Type", "name", "in", ["Aglo M/C", "OLD RP M/C", "RR M/C"]]
                ]
            };
        });
    }
});



frappe.ui.form.on("Reprocess Item", {
    // qty(frm, cdt, cdn) {
    //     let row = locals[cdt][cdn];
    //     if (row.item_code && row.qty) {
    //         frappe.call({
    //             method: "calculate_amount",
    //             doc: frm.doc,
    //             callback: function (r) {
    //                 if (r.message) {
    //                     console.log(r.message);
    //                     frm.refresh_field("item");
    //                 }
    //             },
    //         });
    //     }
    // },
    // basic_rate_as_per_stock_uom(frm, cdt, cdn) {
    //     let row = locals[cdt][cdn];
    //     if (row.item_code && row.qty) {
    //         frappe.call({
    //             method: "calculate_amount",
    //             doc: frm.doc,
    //             callback: function (r) {
    //                 if (r.message) {
    //                     console.log(r.message);
    //                     frm.refresh_field("item");
    //                 }
    //             },
    //         });
    //     }
    // }, 
    qty_bags(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && row.qty_bags && row.std_pkg && row.is_finished_item == 1) {
            row.qty = row.qty_bags * row.std_pkg
            frm.refresh_field("item");
        }
    }, 
    std_pkg(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.item_code && row.qty_bags && row.std_pkg && row.is_finished_item == 1) {
            row.qty = row.qty_bags * row.std_pkg
            frm.refresh_field("item");
        }
    }, 
});