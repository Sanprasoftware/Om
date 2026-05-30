// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

frappe.ui.form.on("Spot GSM", {
    setup(frm) {
        frm.set_query("doctype_hariom", function () {
			return {
				filters: {
					name: ["in", ["Stock Entry", "GD Rewinding"]],
				},
			};
		});
    },
    spot_gsm_type(frm) {
        if (!frm.doc.spot_gsm_item) return;

        frm.doc.spot_gsm_item.forEach(row => {
            row.spot_gsm_type = frm.doc.spot_gsm_type;
        });

        frm.refresh_field("spot_gsm_item");
    },
});
frappe.ui.form.on("SPOT GSM Item", {
    spot_gsm_item_add(frm, cdt, cdn) {
        if (!frm.doc.spot_gsm_type) return;

        frappe.model.set_value(
            cdt,
            cdn,
            "spot_gsm_type",
            frm.doc.spot_gsm_type
        );
    },
    1: calculate_avg,
    2: calculate_avg,
    3: calculate_avg,
    4: calculate_avg,
    5: calculate_avg,
    6: calculate_avg,
    7: calculate_avg,
    8: calculate_avg,
    9: calculate_avg,
    10: calculate_avg,
    11: calculate_avg,
    12: calculate_avg,
    13: calculate_avg,
    14: calculate_avg,
    15: calculate_avg,
    16: calculate_avg,
    17: calculate_avg,
    18: calculate_avg,
    19: calculate_avg,
    20: calculate_avg,
    21: calculate_avg,
    22: calculate_avg,
    23: calculate_avg,
    24: calculate_avg,
    25: calculate_avg,
});
// function calculate_avg(frm, cdt, cdn) {
//     let row = locals[cdt][cdn];
//     let sum = 0, count = 0;
//     let min = null, max = null;
//     for (let i = 1; i <= 25; i++) {
//         if (row[i]) {
//             let val = flt(row[i]);
//             sum += flt(row[i]);
//             count++;
//             if (min === null || val < min) min = val;
//             if (max === null || val > max) max = val;
//         }
//     }
//     frappe.model.set_value(cdt, cdn,"gsm_avg", count ? sum / count : 0);
//     frappe.model.set_value(cdt,cdn,"gsm_vari",(min !== null && max !== null) ? (max - min) : 0);
// }    
function calculate_avg(frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    let sum = 0, count = 0;
    let min = null, max = null;

    for (let i = 1; i <= 25; i++) {
        let val = flt(row[i.toString()]);

        if (val) {
            sum += val;
            count++;

            if (min === null || val < min) min = val;
            if (max === null || val > max) max = val;
        }
    }

    let avg = count ? sum / count : 0;
    let vari = (min !== null && max !== null) ? (max - min) : 0;
    let vari_per = avg ? (vari / avg) * 100 : 0;

    frappe.model.set_value(cdt, cdn, "gsm_avg", avg);
    frappe.model.set_value(cdt, cdn, "gsm_vari", vari);
    frappe.model.set_value(cdt, cdn, "vari", vari_per);
}
