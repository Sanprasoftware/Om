// Custom behavior: when FG qty changes, update scrap items only and keep raw materials unchanged.

frappe.provide("hariom_sanpra.stock_entry");

hariom_sanpra.stock_entry.update_scrap_items = frappe.utils.debounce(function (frm) {
	if (!frm || !frm.doc) return;
	if (!frm.doc.bom_no || !frm.doc.fg_completed_qty) return;
	if (!["Manufacture", "Repack"].includes(frm.doc.purpose)) return;

	return frappe.call({
		method: "hariom_sanpra.stock_entry.get_scrap_items_for_qty",
		args: {
			bom_no: frm.doc.bom_no,
			company: frm.doc.company,
			qty: frm.doc.fg_completed_qty,
			work_order: frm.doc.work_order,
			job_card: frm.doc.job_card,
		},
		callback: function (r) {
			const items = r.message || [];
			if (!items.length) return;

			const by_code = {};
			items.forEach((item) => {
				if (item && item.item_code) by_code[item.item_code] = item;
			});

			const existing_scrap = (frm.doc.items || []).filter((d) => d.is_scrap_item);

			existing_scrap.forEach((row) => {
				const item = by_code[row.item_code];
				if (!item) return;

				frappe.model.set_value(row.doctype, row.name, "qty", item.qty);
				frappe.model.set_value(
					row.doctype,
					row.name,
					"conversion_factor",
					item.conversion_factor || row.conversion_factor || 1
				);
				frappe.model.set_value(
					row.doctype,
					row.name,
					"transfer_qty",
					flt(item.qty) * flt(item.conversion_factor || row.conversion_factor || 1)
				);

				if (item.uom) frappe.model.set_value(row.doctype, row.name, "uom", item.uom);
				if (item.stock_uom)
					frappe.model.set_value(row.doctype, row.name, "stock_uom", item.stock_uom);
				if (item.description)
					frappe.model.set_value(row.doctype, row.name, "description", item.description);
				if (item.item_name)
					frappe.model.set_value(row.doctype, row.name, "item_name", item.item_name);
				if (item.to_warehouse)
					frappe.model.set_value(row.doctype, row.name, "t_warehouse", item.to_warehouse);
				if (item.from_warehouse)
					frappe.model.set_value(row.doctype, row.name, "s_warehouse", item.from_warehouse);
			});

			Object.keys(by_code).forEach((code) => {
				const item = by_code[code];
				if (!existing_scrap.find((r) => r.item_code === code)) {
					let d = frm.add_child("items");
					d.item_code = code;
					d.is_scrap_item = 1;
					d.uom = item.uom || item.stock_uom;
					d.stock_uom = item.stock_uom || item.uom;
					d.conversion_factor = item.conversion_factor || 1;
					d.qty = item.qty;
					d.transfer_qty = flt(d.qty) * flt(d.conversion_factor);
					d.description = item.description;
					d.item_name = item.item_name;
					d.allow_zero_valuation_rate = 1;
					d.t_warehouse = item.to_warehouse || d.t_warehouse;
					d.s_warehouse = item.from_warehouse || d.s_warehouse;
				}
			});

			frm.refresh_field("items");
		},
	});
}, 300);

hariom_sanpra.stock_entry.add_stock_ledger_button = function (frm) {
	if (!frm || !frm.doc || frm.doc.docstatus !== 1) return;

	frm.add_custom_button(
		__("Stock Ledger"),
		function () {
			frappe.route_options = {
				company: frm.doc.company,
				voucher_no: frm.doc.name,
				from_date: frm.doc.posting_date,
				to_date: frm.doc.posting_date,
				work_order: frm.doc.work_order || undefined,
			};
			frappe.set_route("query-report", "Stock Ledger Hariom");
		},
		__("View")
	);
};

function override_fg_completed_qty(frm) {
	if (!frm || frm.__hariom_sanpra_fg_override) return;
	frm.__hariom_sanpra_fg_override = true;

	if (cur_frm && cur_frm.cscript) {
		cur_frm.cscript.fg_completed_qty = function () {
			// Only update scrap items; keep raw material quantities unchanged
			hariom_sanpra.stock_entry.update_scrap_items(frm);
		};
	}
}

frappe.ui.form.on("Stock Entry", {
	custom_mc_run : calc,
	custom_actmtr: calc,
	custom_mtr: calc,
	custom_dtime: calc,
	custom_ld:calc,
	custom_trim:calc,
	custom_other:calc,
	custom_rpm:calc,
	custom_mpm:calc,
	stock_entry_type(frm) {
        if (!frm.doc.stock_entry_type) return;

        (frm.doc.items || []).forEach(row => {
            frappe.model.set_value(
                row.doctype,
                row.name,
                "custom_____stock_entry_type",
                frm.doc.stock_entry_type
            );
        });

		// (frm.doc.custom_raw_items || []).forEach(row => {
        //     frappe.model.set_value(
        //         row.doctype,
        //         row.name,
        //         "stock_entry_type",
        //         frm.doc.stock_entry_type
        //     );
        // });
		
    },
	onload(frm) {
		override_fg_completed_qty(frm);
	},
	refresh(frm) {
		override_fg_completed_qty(frm);
		hariom_sanpra.stock_entry.add_stock_ledger_button(frm);

		frm.set_query("custom_raw_batch", function () {
			return {
				filters: {
					item: frm.doc.custom_raw_item   // or use item_code if needed
				}
			};
		});
		frm.set_query("batch", "custom_raw_items", function (_doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					item: row.item,
				},
			};
		});
		frm.set_query("batch", "custom_rk__small_items", function (_doc, cdt, cdn) {
			const row = locals[cdt][cdn];
			return {
				filters: {
					item: row.item,
				},
			};
		});
		frm.set_query("custom_batch", function () {
			return {
				filters: {
					item: frm.doc.custom_item_code   // or use item_code if needed
				}
			};
		});
		frm.set_query("custom_wastage_batch", function () {
			return {
				filters: {
					item: frm.doc.custom_wastage_item   // or use item_code if needed
				}
			};
		});
	},
	custom_add_data(frm) {
		frm.call({
			method: "hariom_sanpra.public.py.stock_entry.add_items",
			args: {
				doc: frm.doc
			},
			callback: function(r){
				if (r.message && r.message.items) {
					frm.doc.items = r.message.items;
				}
				frm.refresh_field("items");
			}
		})
	},
	custom_rk_add_data(frm) {
		frm.call({
			method: "hariom_sanpra.public.py.stock_entry.add_rk_items",
			args: {
				doc: frm.doc
			},
			callback: function(r){
				if (r.message && r.message.items) {
					frm.doc.items = r.message.items;
				}
				frm.refresh_field("items");
			}
		})
	},
	

});
// ***************************************************************************
function calc(frm) {
	let M = flt(frm.doc.custom_mc_run);
	if(M){
		let target = (M * 45);
		frm.set_value("custom_target_mtr",target);
	}
	// PROD % calculation
    let act = flt(frm.doc.custom_actmtr);
    let tgt = flt(frm.doc.custom_target_mtr);
	let mtr = flt(frm.doc.custom_mtr);
	let dtime = flt(frm.doc.custom_dtime);
	let ld = flt(frm.doc.custom_ld);
	let tiv = flt(frm.doc.total_incoming_value);
	let trim = flt(frm.doc.custom_trim);
	let otr = flt(frm.doc.custom_other);
	let rpm = flt(frm.doc.custom_rpm);
	let mpm = flt(frm.doc.custom_mpm);


    // copy mtr -> actmtr
	if (mtr) {
		frm.set_value("custom_actmtr", mtr);
		act = mtr; // update local variable
	}

	// PROD %
	if (act && tgt) {
		let prod = (act / tgt) * 100;
		frm.set_value("custom_prod_", prod);
	}
	// D.time
	if (dtime){
		let dt = (dtime / 1440) * 100;
		frm.set_value("custom_dtime_",dt); 
	}
	// LD
	if(ld){
		let ld_cal = (ld / tiv) * 100;
		frm.set_value("custom_ld_",ld_cal) 
	}
	if(trim){
		let trim_cal = (trim / 24181) * 100;
		frm.set_value("custom_trim_",trim_cal);
	}
	if(otr){
		let other_cal = (otr / tiv) * 100;
		frm.set_value("custom_other_",other_cal);
	}
	if(rpm && mpm){
		let gram = (rpm * 75 ) / mpm;
		frm.set_value("custom_gram",gram);
		let gsm = (gram * 39.37) / 120;
		frm.set_value("custom_gsm1",gsm);
	}

	
}
// ***************************************************************************

frappe.ui.form.on("Stock Entry Detail", {
    items_add(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.stock_entry_type) {
            frappe.model.set_value(
                cdt,
                cdn,
                "custom_____stock_entry_type",
                frm.doc.stock_entry_type
            );
        }
    }
});

frappe.ui.form.on("Raw Item", {
    item(frm, cdt, cdn) {

        frappe.model.set_value(cdt, cdn, "stock_entry_type", frm.doc.stock_entry_type);

        if (frm.doc.stock_entry_type === "GD REWINDING") {
            frappe.model.set_value(cdt, cdn, "gsm", frm.doc.custom_gsm);
        }

    }
});

frappe.ui.form.on("RK - Small Items", {
    item(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        if (frm.doc.stock_entry_type) {
            frappe.model.set_value(
                cdt,
                cdn,
                "stock_entry_type",
                frm.doc.stock_entry_type
            );
        }
    }
});
