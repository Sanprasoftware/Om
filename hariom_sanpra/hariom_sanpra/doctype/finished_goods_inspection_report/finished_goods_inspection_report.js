// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Finished Goods Inspection Report", {
	finished_goods_inspection_template(frm) {
		frm.clear_table("finished_goods_inspection");

		if (!frm.doc.finished_goods_inspection_template) {
			frm.refresh_field("finished_goods_inspection");
			return;
		}

		const fields = frappe
			.get_meta("Finished Goods Inspection")
			.fields.filter((df) => !frappe.model.no_value_type.includes(df.fieldtype))
			.map((df) => df.fieldname);

		frappe.db
			.get_doc("Finished Goods Inspection Template", frm.doc.finished_goods_inspection_template)
			.then((template) => {
				(template.inspection_parameter || []).forEach((template_row) => {
					const row = frm.add_child("finished_goods_inspection");

					fields.forEach((fieldname) => {
						row[fieldname] = template_row[fieldname];
					});
				});

				frm.refresh_field("finished_goods_inspection");
			});
	},
});
