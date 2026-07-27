// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Finished Goods Inspection Report", {
	// finished_goods_inspection_template(frm) {
	// 	frm.clear_table("finished_goods_inspection");

	// 	if (!frm.doc.finished_goods_inspection_template) {
	// 		frm.refresh_field("finished_goods_inspection");
	// 		return;
	// 	}

	// 	const fields = frappe
	// 		.get_meta("Finished Goods Inspection")
	// 		.fields.filter((df) => !frappe.model.no_value_type.includes(df.fieldtype))
	// 		.map((df) => df.fieldname);

	// 	frappe.db
	// 		.get_doc("Finished Goods Inspection Template", frm.doc.finished_goods_inspection_template)
	// 		.then((template) => {
	// 			(template.inspection_parameter || []).forEach((template_row) => {
	// 				const row = frm.add_child("finished_goods_inspection");

	// 				fields.forEach((fieldname) => {
	// 					row[fieldname] = template_row[fieldname];
	// 				});
	// 			});

	// 			frm.refresh_field("finished_goods_inspection");
	// 		});
	// },
	finished_goods_inspection_template(frm) {

		// Dono tables clear karo
		frm.clear_table("finished_goods_inspection");
		frm.clear_table("inspection_parameter_pipe");
		frm.clear_table("inspection_parameter_murgas");
		frm.clear_table("inspection_parameter_pp_export");

		if (!frm.doc.finished_goods_inspection_template) {
			frm.refresh_fields([
				"finished_goods_inspection",
				"inspection_parameter_pipe",
				"inspection_parameter_murgas",
				"inspection_parameter_pp_export"
			]);
			return;
		}

		frappe.db.get_doc(
			"Finished Goods Inspection Template",
			frm.doc.finished_goods_inspection_template
		).then(template => {

			// Pondline
			if (template.type == "Pondline") {
				(template.inspection_parameter || []).forEach(d => {
					let row = frm.add_child("finished_goods_inspection");
					Object.assign(row, d);
				});
			}

			// Pipe
			if (template.type == "Pipe") {
				(template.inspection_parameter_pipe || []).forEach(d => {
					let row = frm.add_child("inspection_parameter_pipe");
					Object.assign(row, d);
				});
			}

			// Murgas
			if (template.type == "Murgas") {
				(template.inspection_parameter_murgas || []).forEach(d => {
					let row = frm.add_child("inspection_parameter_murgas");
					Object.assign(row, d);
				});
			}

			// PP Export
			if (template.type == "PP Export") {
				(template.inspection_parameter_pp_export || []).forEach(d => {
					let row = frm.add_child("inspection_parameter_pp_export");
					Object.assign(row, d);
				});
			}

			
			frm.refresh_fields([
				"finished_goods_inspection",
				"inspection_parameter_pipe",
				"inspection_parameter_murgas",
				"inspection_parameter_pp_export"
			]);
		});
	},
	onload(frm) {
        set_template_filter(frm);
    },

    type(frm) {
        frm.set_value("finished_goods_inspection_template", "");
        set_template_filter(frm);
    }
});

function set_template_filter(frm) {
    frm.set_query("finished_goods_inspection_template", function() {
        return {
            filters: {
                type: frm.doc.type
            }
        };
    });
}
