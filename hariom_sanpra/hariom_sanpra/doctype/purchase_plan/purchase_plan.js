// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Purchase Plan", {
	date(frm) {
		apply_purchase_plan_formula_for_table(frm, "purchase_plan_item");
		apply_purchase_plan_formula_for_table(frm, "purchase_plan_sub_item");
	},
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
				frm.clear_table("purchase_plan_sub_item");

				(message.items || []).forEach((item) => {
					const row = frm.add_child("purchase_plan_item");
					row.item_code = item.item_code;
					row.stock_kg = flt(item.stock_kg);
					row.required_stock = flt(item.required_stock);
					apply_purchase_plan_item_formula(frm, row.doctype, row.name);
				});

				(message.sub_items || []).forEach((item) => {
					const row = frm.add_child("purchase_plan_sub_item");
					row.item_code = item.item_code;
					row.item_name = item.item_name;
					row.stock_kg = flt(item.stock_kg);
					row.required_stock = flt(item.required_stock);
					apply_purchase_plan_item_formula(frm, row.doctype, row.name);
				});

				frm.refresh_field("purchase_plan_item");
				frm.refresh_field("purchase_plan_sub_item");
			},
		});
	},
});

frappe.ui.form.on("Purchase Plan item", {
	item_code(frm, cdt, cdn) {
		set_purchase_plan_item_stock(frm, cdt, cdn);
	},
	stock_kg(frm, cdt, cdn) {
		apply_purchase_plan_item_formula(frm, cdt, cdn);
	},
	required_stock(frm, cdt, cdn) {
		apply_purchase_plan_item_formula(frm, cdt, cdn);
	},
});

frappe.ui.form.on("Purchase Plan Sub item", {
	item_code(frm, cdt, cdn) {
		set_purchase_plan_item_stock(frm, cdt, cdn);
	},
	stock_kg(frm, cdt, cdn) {
		apply_purchase_plan_item_formula(frm, cdt, cdn);
	},
	required_stock(frm, cdt, cdn) {
		apply_purchase_plan_item_formula(frm, cdt, cdn);
	},
});

function apply_purchase_plan_formula_for_table(frm, table_field) {
	(frm.doc[table_field] || []).forEach((row) => {
		apply_purchase_plan_item_formula(frm, row.doctype, row.name);
	});
	frm.refresh_field(table_field);
}

function set_purchase_plan_item_stock(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	if (!row.item_code) {
		frappe.model.set_value(cdt, cdn, "stock_kg", 0);
		apply_purchase_plan_item_formula(frm, cdt, cdn);
		return;
	}

	frappe.call({
		method: "hariom_sanpra.hariom_sanpra.doctype.purchase_plan.purchase_plan.get_purchase_plan_item_stock",
		args: {
			item_code: row.item_code,
		},
		callback: ({ message }) => {
			frappe.model.set_value(cdt, cdn, "stock_kg", flt(message));
			apply_purchase_plan_item_formula(frm, cdt, cdn);
		},
	});
}

function apply_purchase_plan_item_formula(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	const stock_kg = flt(row.stock_kg);
	const required_stock = flt(row.required_stock);
	const shortage_qty = Math.max(required_stock - stock_kg, 0);

	frappe.model.set_value(cdt, cdn, "shortage_qty", shortage_qty);
	frappe.model.set_value(cdt, cdn, "purchase", required_stock > stock_kg ? "YES" : "NO");
	frappe.model.set_value(cdt, cdn, "target_date", frm.doc.date || frappe.datetime.get_today());
}
