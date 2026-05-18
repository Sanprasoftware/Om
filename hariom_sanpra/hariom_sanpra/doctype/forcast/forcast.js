// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

function set_program_pending(cdt, cdn) {
	const row = locals[cdt][cdn];
	const fgOutputTon = flt(row.fg_output_ton);
	const programComplete = flt(row.program_complete);

	frappe.model.set_value(cdt, cdn, "program_pending", fgOutputTon - programComplete);
}

function set_program_pending_in_row(row) {
	row.program_pending = flt(row.fg_output_ton) - flt(row.program_complete);
}
function set_pending_days_in_row(cdt, cdn) {
	const row = locals[cdt][cdn];
	const pendingDays = flt(row.work_days) - flt(row.program_complete_days);
	frappe.model.set_value(cdt, cdn, "pending_days", pendingDays);
}

function get_table_total(rows, fieldname) {
	return (rows || []).reduce((total, row) => total + flt(row[fieldname]), 0);
}
function set_parent_totals(frm) {
	const totalPlanFg =
		get_table_total(frm.doc.forcast_item, "fg_output_ton") +
		get_table_total(frm.doc.lamination, "fg_output_ton");
	const totalFg =
		get_table_total(frm.doc.forcast_item, "program_complete") +
		get_table_total(frm.doc.lamination, "program_complete");
	const planworkingdays =
		get_table_total(frm.doc.forcast_item, "work_days") +
		get_table_total(frm.doc.lamination, "work_days");
	const totalWorkingDays =
		get_table_total(frm.doc.forcast_item, "pending_days") +
		get_table_total(frm.doc.lamination, "pending_days");
	
	frm.set_value("total_plan_fg", totalPlanFg);
	frm.set_value("total_fg", totalFg);
	frm.set_value("plan_working_days", planworkingdays);
	frm.set_value("total_working_days", totalWorkingDays);

}

frappe.ui.form.on("Forcast", {
	refresh(frm) {
		set_parent_totals(frm);
	},
	get_stock(frm) {
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.doctype.forcast.forcast.get_stock_for_items",
			args: {
				doc: frm.doc,
			},
			freeze: true,
			freeze_message: __("Getting stock..."),
			callback: ({ message }) => {
				if (!message) {
					return;
				}

				["forcast_item", "lamination"].forEach((tablefield) => {
					(frm.doc[tablefield] || []).forEach((row) => {
						row.program_complete = flt(message[row.name]);
						set_program_pending_in_row(row);
					});
					frm.refresh_field(tablefield);
				});

				set_parent_totals(frm);
			},
		});
	},
});

frappe.ui.form.on("JP Forcast Item", {
	fg_output_ton(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		set_parent_totals(frm);
	},
	program_complete(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		set_parent_totals(frm);
	},
	work_days(frm, cdt, cdn) {
		set_pending_days_in_row(cdt, cdn);     // ← YEH LINE ADD KARI
		set_parent_totals(frm);
	},
	// ADDED: program_complete_days event
	program_complete_days(frm, cdt, cdn) {
		set_pending_days_in_row(cdt, cdn); 
		set_parent_totals(frm);
	},
	forcast_item_add(frm) {
		set_parent_totals(frm);
	},
	forcast_item_remove(frm) {
		set_parent_totals(frm);
	},
});
frappe.ui.form.on("Lamination Forcast Item", {
	fg_output_ton(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		set_parent_totals(frm);
	},
	program_complete(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		set_parent_totals(frm);
	},
	work_days(frm, cdt, cdn) {
		set_pending_days_in_row(cdt, cdn);     // ← cdt, cdn pass karo
		set_parent_totals(frm);
	},
	program_complete_days(frm, cdt, cdn) {
		set_pending_days_in_row(cdt, cdn);   
		set_parent_totals(frm);
	},
	lamination_add(frm) {
		set_parent_totals(frm);
	},
	lamination_remove(frm) {
		set_parent_totals(frm);
	},
});
