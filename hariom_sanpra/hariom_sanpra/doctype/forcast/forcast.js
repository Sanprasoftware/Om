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
	frappe.model.set_value(cdt, cdn, "pending_days", pendingDays);
}

function get_table_total(rows, fieldname) {
	return (rows || []).reduce((total, row) => total + flt(row[fieldname]), 0);
}
// function set_parent_totals(frm) {
// 	const totalPlanFg =
// 		get_table_total(frm.doc.forcast_item, "fg_output_ton") +
// 		get_table_total(frm.doc.lamination, "fg_output_ton");

// 	const totalFg =
// 		get_table_total(frm.doc.forcast_item, "program_complete") +
// 		get_table_total(frm.doc.lamination, "program_complete");

// 	const totalProgramPending =
// 		get_table_total(frm.doc.forcast_item, "program_pending") +
// 		get_table_total(frm.doc.lamination, "program_pending");

// 	const planworkingdays =
// 		get_table_total(frm.doc.forcast_item, "work_days") +
// 		get_table_total(frm.doc.lamination, "work_days");

// 	const totalWorkingDays =
// 		get_table_total(frm.doc.forcast_item, "pending_days") +
// 		get_table_total(frm.doc.lamination, "pending_days");

// 	frm.set_value("total_plan_fg", totalPlanFg);
// 	frm.set_value("total_fg", totalFg);
// 	frm.set_value("total_program_pending_ton", totalProgramPending);
// 	frm.set_value("plan_working_days", planworkingdays);
// 	frm.set_value("total_working_days", totalWorkingDays);
// }
function set_work_days(cdt, cdn) {
	let row = locals[cdt][cdn];
	if (flt(row.per_day_production) > 0) {
		frappe.model.set_value(cdt, cdn, "work_days", flt(row.fg_output_ton) / flt(row.per_day_production));
	}
}
function set_pending_days(cdt, cdn) {
	let row = locals[cdt][cdn];
	if (flt(row.per_day_production) > 0) {
		frappe.model.set_value(cdt, cdn, "pending_days", flt(row.program_pending) / flt(row.per_day_production));
	}
}
frappe.ui.form.on("Forcast", {
	refresh(frm) {
		// set_parent_totals(frm);
		calculate_total_forcast_item(frm);
		calculate_total_lamination_item(frm);
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

				// set_parent_totals(frm);
			},
		});
	},
});

frappe.ui.form.on("JP Forcast Item", {
	fg_output_ton(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		set_work_days(cdt, cdn);
		// set_parent_totals(frm);
		set_pending_days(cdt, cdn); 
		calculate_total_forcast_item(frm);  
	},
	per_day_production(frm, cdt, cdn) { 
		set_work_days(cdt, cdn);
		set_pending_days(cdt, cdn);
		// set_parent_totals(frm);
		calculate_total_forcast_item(frm);
		
	},
	program_complete(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		set_pending_days(cdt, cdn);   
		// set_parent_totals(frm);
		calculate_total_forcast_item(frm);
	},
	
	work_days(frm, cdt, cdn) {
		set_pending_days_in_row(cdt, cdn);
		// set_parent_totals(frm);
		calculate_total_forcast_item(frm);
	},
	forcast_item_add(frm) {
		// set_parent_totals(frm);
		calculate_total_forcast_item(frm);
	},
	forcast_item_remove(frm) {
		// set_parent_totals(frm);
		calculate_total_forcast_item(frm);
	},
});
frappe.ui.form.on("Lamination Forcast Item", {
	fg_output_ton(frm, cdt, cdn) {
		set_work_days(cdt, cdn);
		set_program_pending(cdt, cdn);
		// set_parent_totals(frm);
		set_pending_days(cdt, cdn); 
		calculate_total_lamination_item(frm); 
	},
	per_day_production(frm, cdt, cdn) { // ← ADD KIYA
		set_work_days(cdt, cdn);
		// set_parent_totals(frm);
		set_pending_days(cdt, cdn); 
		calculate_total_lamination_item(frm);  
	},
	program_complete(frm, cdt, cdn) {
		set_program_pending(cdt, cdn);
		// set_parent_totals(frm);
		set_pending_days(cdt, cdn);   
		calculate_total_lamination_item(frm);
	},
	work_days(frm, cdt, cdn) {
		set_pending_days_in_row(cdt, cdn);     
		// set_parent_totals(frm);
		calculate_total_lamination_item(frm);
	},
	lamination_add(frm) {
		// set_parent_totals(frm);
		calculate_total_lamination_item(frm);
	},
	lamination_remove(frm) {
		// set_parent_totals(frm);
		calculate_total_lamination_item(frm);
	},
});



// **********************************************forcast_item calculation**************************************************
function calculate_total_forcast_item(frm) {
    let total_fg = 0;
    let total_days = 0;
	let total_prog_comp = 0;
	let total_prog_pending = 0;
	let total_prog_pending_days = 0;

    (frm.doc.forcast_item || []).forEach(row => {
        total_fg += flt(row.fg_output_ton);
        total_days += flt(row.work_days);
		total_prog_comp += flt(row.program_complete);
		total_prog_pending += flt(row.program_pending);
		total_prog_pending_days += flt(row.pending_days);
    });

    frm.set_value("total_plan_fg_kg1", total_fg);
    frm.set_value("planned_working_days1", total_days);
	frm.set_value("total_program_completed_fg_kg1", total_prog_comp);
	frm.set_value("total_program_pending_kg1", total_prog_pending);
	frm.set_value("total_pending_days1", total_prog_pending_days);
}

// **********************************************lamination calculation************************************************************

function calculate_total_lamination_item(frm) {
    let total_lami1 = 0;
    let total_days1 = 0;
	let total_prog_comp1 = 0;
	let total_prog_pending1 = 0;
	let total_prog_pending_days1 = 0;

    (frm.doc.lamination || []).forEach(row => {
        total_lami1 += flt(row.fg_output_ton);
        total_days1 += flt(row.work_days);
		total_prog_comp1 += flt(row.program_complete);
		total_prog_pending1 += flt(row.program_pending);
		total_prog_pending_days1 += flt(row.pending_days);
    });

    frm.set_value("total_plan_fg", total_lami1);
    frm.set_value("plan_working_days", total_days1);
	frm.set_value("total_fg", total_prog_comp1);
	frm.set_value("total_program_pending_ton", total_prog_pending1);
	frm.set_value("total_working_days", total_prog_pending_days1);
}


