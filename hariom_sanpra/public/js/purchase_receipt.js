frappe.ui.form.on("Purchase Receipt", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1) {
			return;
		}

		frm.add_custom_button(__("Quality Inspection"), () => {
			frappe.route_options = {
				inspection_type: "Incoming",
				reference_type: "Purchase Receipt",
				reference_name: frm.doc.name,
				company: frm.doc.company,
				report_date: frappe.datetime.nowdate(),
			};

			frappe.new_doc("Quality Inspection");
		});
	},
});
