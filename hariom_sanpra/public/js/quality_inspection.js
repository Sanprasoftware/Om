frappe.ui.form.on("Quality Inspection", {
	setup(frm) {
		set_item_query(frm);
	},


	reference_name(frm) {
		set_reference_details(frm);
	},

	reference_type(frm) {
		set_reference_details(frm);
	},
});

function set_reference_details(frm) {
	if (!frm.doc.reference_type || !frm.doc.reference_name) {
		clear_purchase_receipt_details(frm);
		clear_delivery_note_details(frm);
		return;
	}

	if (frm.doc.reference_type === "Purchase Receipt") {
		clear_delivery_note_details(frm);
		set_purchase_receipt_details(frm);
		return;
	}

	if (frm.doc.reference_type === "Delivery Note") {
		clear_purchase_receipt_details(frm);
		set_delivery_note_details(frm);
		return;
	}

	clear_purchase_receipt_details(frm);
	clear_delivery_note_details(frm);
}

function clear_purchase_receipt_details(frm) {
	set_value_if_changed(frm, "custom_supplier_name", "");
	set_value_if_changed(frm, "custom_pr_date", "");
}

function clear_delivery_note_details(frm) {
	set_value_if_changed(frm, "custom_customer_name", "");
	set_value_if_changed(frm, "custom_delivery_date", "");
}

function set_value_if_changed(frm, fieldname, value) {
	if ((frm.doc[fieldname] || "") !== (value || "")) {
		frm.set_value(fieldname, value);
	}
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

			set_value_if_changed(frm, "custom_supplier_name", r.supplier_name || r.supplier);
			set_value_if_changed(frm, "custom_pr_date", r.posting_date);
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

			set_value_if_changed(frm, "custom_customer_name", r.customer_name || r.customer);
			set_value_if_changed(frm, "custom_delivery_date", r.posting_date);
		}
	);
}


function set_item_query(frm) {
	frm.set_query("item_code", function (doc) {
		let doctype = doc.reference_type;

		if (doc.reference_type !== "Job Card") {
			doctype = doc.reference_type === "Stock Entry" ? "Stock Entry Detail" : doc.reference_type + " Item";
		}

		if (doc.reference_type && doc.reference_name) {
			let filters = {
				from: doctype,
				inspection_type: doc.inspection_type,
			};

			if (doc.reference_type === doctype) {
				filters.reference_name = doc.reference_name;
			} else {
				filters.parent = doc.reference_name;
			}

			return {
				query: "hariom_sanpra.public.py.quality_inspection.item_query",
				filters: filters,
			};
		}
	});
}

// ***********************************************calculate custom_reading_avg**************************************************
function calculate_average(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let total = 0;
    let count = 0;
    for (let i = 1; i <= 10; i++) {
		let value = row[`reading_${i}`];

		if (value !== undefined && value !== null && value !== "") {
			total += flt(value);
			count++;
		}
	}
    frappe.model.set_value(
        cdt,
        cdn,
        "custom_reading_avg",
        count ? (total / count) : 0
    );
}
frappe.ui.form.on("Quality Inspection Reading", {
    reading_1: calculate_average,
    reading_2: calculate_average,
    reading_3: calculate_average,
    reading_4: calculate_average,
    reading_5: calculate_average,
    reading_6: calculate_average,
    reading_7: calculate_average,
    reading_8: calculate_average,
    reading_9: calculate_average,
    reading_10: calculate_average
});
