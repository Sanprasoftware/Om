frappe.ui.form.on("Purchase Receipt", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1) {
			return;
		}

		frm.add_custom_button(__("Material Hold"), () => {
			frappe.route_options = {
				reference_doc: frm.doc.doctype,
				reference_id: frm.doc.name,
			};

			frappe.new_doc("Material Hold");
		});
		frm.add_custom_button(__("Quality Inspection"), () => {
			frappe.route_options = {
				inspection_type: "Incoming",
				reference_type: "Purchase Receipt",
				reference_name: frm.doc.name,
				company: frm.doc.company,
				report_date: frappe.datetime.nowdate(),
				custom_supplier_name: frm.doc.supplier,
				custom_pr_date: frm.doc.posting_date,
			};

			frappe.new_doc("Quality Inspection");
		});
	},
});
