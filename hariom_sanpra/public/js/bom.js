frappe.ui.form.on("BOM", {
	quantity(frm) {
		(frm.doc.items || []).forEach((row) => set_bom_percent(frm, row));
	},
});

frappe.ui.form.on("BOM Item", {
	qty(frm, cdt, cdn) {
		set_bom_percent(frm, locals[cdt][cdn]);
	},
});

function set_bom_percent(frm, row) {
	const bom_qty = flt(frm.doc.quantity);
	const percent = bom_qty ? (flt(row.qty) / bom_qty) * 100 : 0;

	frappe.model.set_value(
		row.doctype,
		row.name,
		"custom_bom_percent_rm",
		percent
	);
}