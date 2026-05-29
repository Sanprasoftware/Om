// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("delivery challan", {
	refresh(frm) {
		set_status_indicator(frm);

		if (frm.doc.docstatus == 1 && frm.doc.type === "OUT" && frm.doc.status !== "Completed") {
			frm.add_custom_button(__("Delivery Challan In"), () => {
				frappe.new_doc("delivery challan", {
					ref_doc: frm.doc.name,
					type: "IN",
					employee_name: frm.doc.employee_name
				}, doc => {
					frm.doc.items.forEach(row => {
						let child = frappe.model.add_child(doc, "items");
						child.source_warehouse = row.target_warehouse;
						child.target_warehouse = row.source_warehouse;
						child.item_code = row.item_code;
						child.uom = row.uom;

					});
				});
			}, __("Create"));
		}
	}
});
frappe.ui.form.on("delivery challan Items", {
    
    // Jab Qty change ho
    qty: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    },
    
    // Jab Rate change ho  
    rate: function(frm, cdt, cdn) {
        calculate_amount(frm, cdt, cdn);
    }
});

// Amount calculate karne ka function
function calculate_amount(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.qty && row.rate) {
        let amount = row.qty * row.rate;
        frappe.model.set_value(cdt, cdn, "amount", amount);
    }
}
function set_status_indicator(frm) {
	if (frm.doc.type !== "OUT" || frm.doc.docstatus !== 1 || !frm.doc.status) {
		return;
	}

	const colors = {
		Pending: "orange",
		Partially: "orange",
		Completed: "green"
	};

	frm.page.set_indicator(__(frm.doc.status), colors[frm.doc.status] || "gray");
}
