// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("First Sheet Approval", {
    refresh(frm) {
        calculate_total(frm);
    },
    a_total_qty: function(frm) {
        calculate_percent(frm);
    },
    b_total_qty: function(frm) {
        calculate_percent(frm);
    },
    mc_type(frm) {
        if (!frm.doc.mc_type) return;

        (frm.doc.extruder || []).forEach(row => {
            frappe.model.set_value(
                row.doctype,
                row.name,
                "mc_type",
                frm.doc.mc_type
            );
        });
		
    },
});
frappe.ui.form.on("Extruder", {
    a_qty(frm) {
        calculate_total(frm);
        calculate_percent(frm);
    },
    a_percent(frm) {
        calculate_total(frm);
    },
    b_qty(frm) {
        calculate_total(frm);
        calculate_percent(frm);
    },
    b_percent(frm) {
        calculate_total(frm);
    },
    extruder_remove: function(frm) {
        calculate_total(frm);
        calculate_percent(frm);

        frm.refresh_field("a_total_qty");
        frm.refresh_field("extruder");
    },
    extruder_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.mc_type) {
            frappe.model.set_value(
                cdt,
                cdn,
                "mc_type",
                frm.doc.mc_type
            );
        }
    }
});
// 8******************************************************************************
function calculate_percent(frm) {
    frm.doc.extruder.forEach(function(row) {
        row.a_percent = frm.doc.a_total_qty
            ? (flt(row.a_qty) / flt(frm.doc.a_total_qty)) * 100
            : 0;
        row.b_percent = frm.doc.b_total_qty
            ? (flt(row.b_qty) / flt(frm.doc.b_total_qty)) * 100
            : 0;
    });

    frm.refresh_field("extruder");
}
// 8******************************************************************************
function calculate_total(frm) {
    let a_qty = 0,
        a_percent = 0,
        b_qty = 0,
        b_percent = 0;
    (frm.doc.extruder || []).forEach(d => {
        a_qty += flt(d.a_qty);
        a_percent += flt(d.a_percent);
        b_qty += flt(d.b_qty);
        b_percent += flt(d.b_percent);
    });
    frm.set_value("a_total_qty", a_qty);
    frm.set_value("a_total_", a_percent);
    frm.set_value("b_total_qty", b_qty);
    frm.set_value("b_toal_", b_percent);
}