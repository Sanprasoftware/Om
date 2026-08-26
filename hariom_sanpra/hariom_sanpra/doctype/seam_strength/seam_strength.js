// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Seam Strength", {
    setup(frm) {
        frm.set_query("doctype_hariom", function () {
			return {
				filters: {
					name: ["in", ["Joint Machine", "Small Pipe MC"]],
				},
			};
		});
    },
    seam_strength_type: function(frm) {
        // if (frm.doc.seam_strength_type === "Joint M/C") {
        //     frm.set_value("overlap_req", "50 MM");
        // }
        // if (frm.doc.seam_strength_type === "Pipe") {
        //     frm.set_value("overlap_req", "20 MM");
        // }
        if (frm.doc.seam_strength_reading) {
            frm.doc.seam_strength_reading.forEach(row => {
                row.seam_strength_type = frm.doc.seam_strength_type;
            });

            // 🔥 VERY IMPORTANT
            frm.refresh_field("seam_strength_reading");
        }
    }
});
frappe.ui.form.on("Seam Strength Child", {
    seam_strength_reading_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (frm.doc.seam_strength_type) {
            row.seam_strength_type = frm.doc.seam_strength_type;
            frm.refresh_field("seam_strength_reading");
        }
    },
    jm_brand_type: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.jm_brand_type === "300 MIC") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "15 N / MM");
            frappe.model.set_value(cdt, cdn, "overlap_req", "50 MM");
        }
        if (row.jm_brand_type === "400 MIC") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "25 N / MM");
            frappe.model.set_value(cdt, cdn, "overlap_req", "50 MM");
        }
        if (row.jm_brand_type === "500 MIC") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "37 N / MM");
            frappe.model.set_value(cdt, cdn, "overlap_req", "50 MM");
        }
        if (row.jm_brand_type === "750 MIC") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "40 N / MM");
            frappe.model.set_value(cdt, cdn, "overlap_req", "50 MM");
        }
        if (row.jm_brand_type === "1000 MIC") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "");
            frappe.model.set_value(cdt, cdn, "overlap_req", "50 MM");
        }
    },
    pipe_brand_type: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (row.pipe_brand_type === "220 GSM") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "13 N / MM");
            frappe.model.set_value(cdt, cdn, "hidrostatic", 1.5);
            frappe.model.set_value(cdt, cdn, "overlap_req", "20 MM");
        }
        if (row.pipe_brand_type === "250 GSM") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "13 N / MM");
            frappe.model.set_value(cdt, cdn, "hidrostatic", 1.5);
            frappe.model.set_value(cdt, cdn, "overlap_req", "20 MM");
        }
        if (row.pipe_brand_type === "190 GSM") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "10 N / MM");
            frappe.model.set_value(cdt, cdn, "hidrostatic", 1.5);
            frappe.model.set_value(cdt, cdn, "overlap_req", "20 MM");
        }
        if (row.pipe_brand_type === "170 GSM") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "10 N / MM");
            frappe.model.set_value(cdt, cdn, "hidrostatic", 1.5);
            frappe.model.set_value(cdt, cdn, "overlap_req", "20 MM");
        }
        if (row.pipe_brand_type === "105 GSM") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "7 N / MM");
            frappe.model.set_value(cdt, cdn, "hidrostatic", "");
            frappe.model.set_value(cdt, cdn, "overlap_req", "12 MM");
        }
        if (row.pipe_brand_type === "400 GSM") {
            frappe.model.set_value(cdt, cdn, "sample_target_strength_req", "23 N / MM");
            frappe.model.set_value(cdt, cdn, "hidrostatic", 3.8);
            frappe.model.set_value(cdt, cdn, "overlap_req", "20 MM");
        }
        
    },
    sample_overlap_req_1: calc_avg,
    sample_overlap_req_2: calc_avg,
    sample_overlap_req_3: calc_avg,

    sample_strength_req_1: calc_avg,
    sample_strength_req_2: calc_avg,
    sample_strength_req_3: calc_avg
    
});

function calc_avg(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let overlap_avg = (
        flt(row.sample_overlap_req_1) +
        flt(row.sample_overlap_req_2) +
        flt(row.sample_overlap_req_3)
    ) / 3;
    frappe.model.set_value(cdt, cdn, "sample_overlap_req_avg", overlap_avg);
    let strength_avg = (
        flt(row.sample_strength_req_1) +
        flt(row.sample_strength_req_2) +
        flt(row.sample_strength_req_3)
    ) / 3;
    frappe.model.set_value(cdt, cdn, "sample_strength_req_avg", strength_avg);
}