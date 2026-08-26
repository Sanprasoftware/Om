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
		show_reprocess_entry_fields(frm);

		frm.fields_dict["item"].grid.get_field("batch_no").get_query = function(doc, cdt, cdn) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					item: row.item_code,
                    // docstatus: 1
				}
			};
		};

		// frm.fields_dict["scrap_item"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
		// 	let row = locals[cdt][cdn];

		// 	return {
		// 		filters: {
		// 			item: row.item_code,
        //             docstatus: 1
		// 		}
		// 	};
		// };
        
		// frm.fields_dict["fg_item"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
		// 	let row = locals[cdt][cdn];

		// 	return {
		// 		filters: {
		// 			item: row.item_code,
        //             docstatus: 1
		// 		}
		// 	};
		// };
		// frm.fields_dict["wastage"].grid.get_field("batch").get_query = function(doc, cdt, cdn) {
		// 	let row = locals[cdt][cdn];

		// 	return {
		// 		filters: { 
		// 			item: row.item_code,
        //             docstatus: 1
		// 		}
		// 	};
		// };
	},

    setup(frm) {
        frm.set_query("stock_entry_type", function () {
            return {
                filters: [
                    ["Stock Entry Type", "purpose", "=", "Repack"],
                    ["Stock Entry Type", "name", "in", ["Old RP MC", "RR MC"]]
                ]
            };
        });
    },

    // onload(frm) {
    //   frm.set_query("batch_no", "item", function(doc, cdt, cdn) {
    //     const row = locals[cdt][cdn];
    //     if (!row.item_code) {
    //       return { filters: { name: "" } }; // no item selected
    //     }
    //     return {
    //       filters: {
    //         item: row.item_code,
    //         // docstatus: 1

    //       }
    //     };
    //   }); 
    // }
});

const reprocess_entry_fields = [
	"operator_names",
	"shift",
	"mc__start",
	"downtime_reason",
	"mesh_used",
	"mc_stop",
	"other_abrnormality"
];

function show_reprocess_entry_fields(frm) {
	reprocess_entry_fields.forEach((fieldname) => {
		if (!frm.get_field(fieldname)) {
			return;
		}

		frm.set_df_property(fieldname, "hidden", 0);
		frm.set_df_property(fieldname, "read_only", frm.doc.docstatus === 1 ? 1 : 0);
		frm.toggle_display(fieldname, true);
	});
}


frappe.ui.form.on("Reprocess Item", {
    qty_bags(frm, cdt, cdn) {
        update_qty(frm, cdt, cdn);
    },

    std_pkg(frm, cdt, cdn) {
        update_qty(frm, cdt, cdn);
    },

    is_finished_item(frm, cdt, cdn) {
        update_qty(frm, cdt, cdn);
    },

    item_code(frm, cdt, cdn) {
        update_qty(frm, cdt, cdn);
        get_stock(frm, cdt, cdn);
    },

    source_warehouse(frm, cdt, cdn) {
        get_stock(frm, cdt, cdn);
    },
    
});
function update_qty(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.item_code && row.qty_bags && row.std_pkg && row.is_finished_item == 1) {
        row.qty = row.qty_bags * row.std_pkg;
        frm.refresh_field("item");
    }
}

function get_stock(frm, cdt, cdn) {
    let row = locals[cdt][cdn];

    if (row.item_code && row.source_warehouse) {
        frappe.db.get_value("Bin", { item_code: row.item_code, warehouse: row.source_warehouse }, "actual_qty")
            .then(r => {
                if (r.message) {
                    console.log(r.message);
                    row.available_stock = r.message.actual_qty;
                    frm.refresh_field("item");
                }
            });
    }
}