// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Plan", {
	onload(frm) {
        frm.set_query("item_code", "marketing_order", function(doc, cdt, cdn) {
            return {
                filters: {
                    default_bom: ["!=", ""]  // Only items where default_bom is not empty
                }
            };
        });
    },
	check_material(frm) {
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.doctype.purchase_plan.purchase_plan.get_purchase_plan_materials",
			args: {
				doc: frm.doc,
			},
			freeze: true,
			freeze_message: __("Checking materials..."),
			callback: ({ message }) => {
				if (!message) {
					return;
				}

				frm.clear_table("purchase_plan_item");

				(message || []).forEach((item) => {
					const row = frm.add_child("purchase_plan_item");
					row.item_code = item.item_code;
					row.stock_kg = flt(item.stock_kg);
					row.required_stock = flt(item.required_stock);
					row.shortage_qty = flt(item.shortage_qty);
					row.purchase = item.purchase;
				});

				frm.refresh_field("purchase_plan_item");
			},
		});
	},
});
