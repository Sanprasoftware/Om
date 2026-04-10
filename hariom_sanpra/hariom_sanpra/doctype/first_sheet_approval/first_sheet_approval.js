// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("First Sheet Approval", {
    refresh(frm) {
        calculate_total(frm);
    }
});
frappe.ui.form.on("Extruder", {
    a_qty(frm) {
        calculate_total(frm);
    },
    a_percent(frm) {
        calculate_total(frm);
    },
    b_qty(frm) {
        calculate_total(frm);
    },
    b_percent(frm) {
        calculate_total(frm);
    },
    remove(frm) {
        calculate_total(frm);
    }
});

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