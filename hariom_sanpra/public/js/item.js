
frappe.ui.form.on("Item", {
	refresh(frm) {
		frm.set_query("custom_batch", function () {
			return {
				filters: {
					item: frm.doc.name
				}
			};
		});
	},
});
