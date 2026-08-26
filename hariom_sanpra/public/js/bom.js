frappe.ui.form.on("BOM", {
	custom_total_rm_qty(frm) {
		(frm.doc.items || []).forEach((row) => set_bom_percent(frm, row));
		update_total_bom_percent(frm);
	},
});

frappe.ui.form.on("BOM Item", {
	qty(frm, cdt, cdn) {
		set_bom_percent(frm, locals[cdt][cdn]);
		update_total_bom_percent(frm);
	},
	custom_bom_percent_rm(frm) {
		update_total_bom_percent(frm);
	},
});

function set_bom_percent(frm, row) {
	const bom_qty = flt(frm.doc.custom_total_rm_qty);
	const percent = bom_qty ? (flt(row.qty) / bom_qty) * 100 : 0;

	frappe.model.set_value(
		row.doctype,
		row.name,
		"custom_bom_percent_rm",
		percent
	);
}
function update_total_bom_percent(frm) {
	let total = 0;

	(frm.doc.items || []).forEach((row) => {
		total += flt(row.custom_bom_percent_rm);
	});

	frm.set_value("custom_bom__rm_percent_", total);
}