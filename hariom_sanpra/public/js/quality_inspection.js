frappe.ui.form.on("Quality Inspection", {
	refresh(frm) {
		set_reference_details(frm);
	},

	reference_name(frm) {
		set_reference_details(frm);
	},

	reference_type(frm) {
		set_reference_details(frm);
	},
});

function set_reference_details(frm) {
	clear_purchase_receipt_details(frm);
	clear_delivery_note_details(frm);

	if (!frm.doc.reference_type || !frm.doc.reference_name) {
		return;
	}

	if (frm.doc.reference_type === "Purchase Receipt") {
		set_purchase_receipt_details(frm);
		return;
	}

	if (frm.doc.reference_type === "Delivery Note") {
		set_delivery_note_details(frm);
	}
}

function clear_purchase_receipt_details(frm) {
	frm.set_value("custom_supplier_name", "");
	frm.set_value("custom_pr_date", "");
}

function clear_delivery_note_details(frm) {
	frm.set_value("custom_customer_name", "");
	frm.set_value("custom_delivery_date", "");
}

function set_purchase_receipt_details(frm) {
	frappe.db.get_value(
		"Purchase Receipt",
		frm.doc.reference_name,
		["supplier", "supplier_name", "posting_date"],
		(r) => {
			if (!r) {
				return;
			}

			frm.set_value("custom_supplier_name", r.supplier_name || r.supplier);
			frm.set_value("custom_pr_date", r.posting_date);
		}
	);
}

function set_delivery_note_details(frm) {
	frappe.db.get_value(
		"Delivery Note",
		frm.doc.reference_name,
		["customer", "customer_name", "posting_date"],
		(r) => {
			if (!r) {
				return;
			}

			frm.set_value("custom_customer_name", r.customer_name || r.customer);
			frm.set_value("custom_delivery_date", r.posting_date);
		}
	);
}
