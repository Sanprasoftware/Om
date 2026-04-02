// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Plan", {
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
				});

				frm.refresh_field("purchase_plan_item");
			},
		});
	},
});
