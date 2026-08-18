// Copyright (c) 2026, Sanpra Software Solution and contributors
// For license information, please see license.txt

const FABRIC_REPORT_STOCK_METHOD =
	"hariom_sanpra.hariom_sanpra.doctype.fabric_report.fabric_report.get_fabric_stock";

frappe.ui.form.on("FABRIC STOCK Items", {
	gsm(frm, cdt, cdn) {
		fetch_width_stock(cdt, cdn, "gsm", {
			"6": "6ft_kg",
			"10": "10_ft_kg",
			"11": "11_ft_kg",
			"12": "12_ft_kg",
		}, "totalkg", "f_goutput_kg");
	},
	"6ft_kg": function(frm) {
		update_total(frm);
	},
	"10_ft_kg": function(frm) {
		update_total(frm);
	},
	"11_ft_kg": function(frm) {
		update_total(frm);
	},
	"12_ft_kg": function(frm) {
		update_total(frm);
	},
	totalkg : function(frm) {
		update_total(frm);
	},
	f_goutput_kg : function(frm) {
		update_total(frm);
	},
	fabric_stock_items_remove(frm) {
		update_total(frm);
	}
});

frappe.ui.form.on("UNLAM SULZER FABRIC Items", {
	gsm(frm, cdt, cdn) {
		fetch_width_stock(cdt, cdn, "gsm", {
			"6": "6ft_kg",
			"10": "10_ft_kg",
			"12": "12_ft_kg",
		}, "totalkg", "f_goutput_kg");
	},
	"6ft_kg": function(frm) {
		update_total_2(frm);
	},
	"10_ft_kg": function(frm) {
		update_total_2(frm);
	},
	"12_ft_kg": function(frm) {
		update_total_2(frm);
	},
	totalkg : function(frm) {
		update_total_2(frm);
	},
	f_goutput_kg : function(frm) {
		update_total_2(frm);
	},
	unlam_sulzer_fabric_items_remove(frm) {
		update_total_2(frm);
	}
});

frappe.ui.form.on("UNLAM  OTHER POND FABRIC Items", {
	gsm(frm, cdt, cdn) {
		fetch_width_stock(cdt, cdn, "gsm", {
			"6": "6ft_kg",
			"10": "10_ft_kg",
			"11": "11_ft_kg",
			"12": "12_ft_kg",
		}, "totalkg", "f_goutput_kg");
	},
	"6ft_kg": function(frm) {
		update_total_3(frm);
	},
	"10_ft_kg": function(frm) {
		update_total_3(frm);
	},
	"11_ft_kg": function(frm) {
		update_total_3(frm);
	},
	"12_ft_kg": function(frm) {
		update_total_3(frm);
	},
	totalkg : function(frm) {
		update_total_3(frm);
	},
	f_goutput_kg : function(frm) {
		update_total_3(frm);
	},
	unlam__other_pond_fabric_items_remove(frm) {
		update_total_3(frm);
	}
});

frappe.ui.form.on("UNLAM PIPE STOCK Items", {
	gsm(frm, cdt, cdn) {
		fetch_width_stock(cdt, cdn, "gsm", {
			"6": "6ft_kg",
			"7.5": "75_ft_kg",
			"8.3": "83_ft_kg",
		}, "totalkg", "f_goutput_kg");
	},
	"6ft_kg": function(frm) {
		update_total_4(frm);
	},
	"83_ft_kg": function(frm) {
		update_total_4(frm);
	},
	"75_ft_kg": function(frm) {
		update_total_4(frm);
	},
	totalkg : function(frm) {
		update_total_4(frm);
	},
	f_goutput_kg : function(frm) {
		update_total_4(frm);
	},
	unlam_pipe_stock_items_remove(frm) {
		update_total_4(frm);
	}
});

frappe.ui.form.on("PP EXPORT UNLAM  FAB STOCK", {
	gsm__fab(frm, cdt, cdn) {
		fetch_width_stock(cdt, cdn, "gsm__fab", {
			"12": "12_ft",
			"8.3": "83_ft",
		}, "totalkg", "f_g_outputkg");
	},
	"12_ft": function(frm) {
		update_total_5(frm);
	},
	"83_ft": function(frm) {
		update_total_5(frm);
	},
	totalkg : function(frm) {
		update_total_5(frm);
	},
	f_g_outputkg : function(frm) {
		update_total_5(frm);
	},
	pp_export_unlam__fab_stock_items_remove(frm) {
		update_total_5(frm);
	}
});

frappe.ui.form.on("PP EXPORT NON STOCK Items", {
	gsm(frm, cdt, cdn) {
		fetch_or_calculate_non_stock_item(cdt, cdn);
	},
	feet(frm, cdt, cdn) {
		fetch_or_calculate_non_stock_item(cdt, cdn);
	},
	qty_kg(frm, cdt, cdn) {
		calculate_non_stock_totals(cdt, cdn);
		update_total_6(frm);
	},
	total_kg : function(frm) {
		update_total_6(frm);
	},
	fg__output_kg : function(frm) {
		update_total_6(frm);
	},
	pp_export_non_stock_items_remove(frm) {
		update_total_6(frm);
	}
});

function fetch_width_stock(cdt, cdn, gsm_field, width_fields, total_field, output_field) {
	const row = locals[cdt][cdn];
	const gsm = row[gsm_field];
	const fields = [...Object.values(width_fields), total_field, output_field];

	if (!gsm) {
		set_stock_values(cdt, cdn, fields, {});
		return;
	}

	frappe.call({
		method: FABRIC_REPORT_STOCK_METHOD,
		args: { gsm, report_date: cur_frm.doc.date },
		freeze: true,
		freeze_message: __("Fetching remaining fabric stock..."),
		callback(r) {
			if (locals[cdt]?.[cdn]?.[gsm_field] !== gsm) return;

			const stock = r.message || {};
			const values = {};
			let total = 0;
			Object.entries(width_fields).forEach(([width, fieldname]) => {
				values[fieldname] = flt(stock[width]);
				total += values[fieldname];
			});
			values[total_field] = flt(total, 2);
			values[output_field] = flt(total / get_output_divisor(cdt, gsm), 2);
			set_stock_values(cdt, cdn, fields, values);
		},
	});
}

function fetch_or_calculate_non_stock_item(cdt, cdn) {
	const row = locals[cdt][cdn];
	if (row.gsm && row.feet) {
		fetch_non_stock_item(cdt, cdn);
	} else {
		calculate_non_stock_totals(cdt, cdn);
	}
}

function calculate_non_stock_totals(cdt, cdn) {
	const row = locals[cdt][cdn];
	const total = flt(row.qty_kg, 2);
	frappe.model.set_value(cdt, cdn, "total_kg", total);
	frappe.model.set_value(
		cdt,
		cdn,
		"fg__output_kg",
		flt(total / get_output_divisor(cdt, row.gsm, row.feet), 2),
	);
}

function fetch_non_stock_item(cdt, cdn) {
	const row = locals[cdt][cdn];
	const gsm = row.gsm;
	const feet = row.feet;
	const fields = ["qty_kg", "total_kg", "fg__output_kg"];

	if (!gsm || !feet) {
		set_stock_values(cdt, cdn, fields, {});
		return;
	}

	frappe.call({
		method: FABRIC_REPORT_STOCK_METHOD,
		args: { gsm, report_date: cur_frm.doc.date, feet },
		freeze: true,
		freeze_message: __("Fetching remaining fabric stock..."),
		callback(r) {
			const current_row = locals[cdt]?.[cdn];
			if (!current_row || current_row.gsm !== gsm || current_row.feet !== feet) return;
			const values = r.message || {};
			values.total_kg = flt(values.qty_kg);
			values.fg__output_kg = flt(
				values.total_kg / get_output_divisor(cdt, gsm, feet),
				2,
			);
			set_stock_values(cdt, cdn, fields, values);
		},
	});
}

function set_stock_values(cdt, cdn, fields, values) {
	fields.forEach((fieldname) => {
		frappe.model.set_value(cdt, cdn, fieldname, flt(values[fieldname]));
	});
}

function get_output_divisor(child_doctype, gsm, feet = null) {
	gsm = (gsm || "").trim().toUpperCase();

	if (child_doctype === "UNLAM SULZER FABRIC Items" && gsm === "245 SULZER") {
		return 0.60;
	}

	if (child_doctype === "UNLAM PIPE STOCK Items") {
		if (["58 GSM","55 GSM","60 GSM"].includes(gsm)) return 0.50;
		if (["75 GSM", "55 BLUE CHEX"].includes(gsm)) return 0.45;
	}

	if (child_doctype === "PP EXPORT UNLAM  FAB STOCK") {
		return 0.42;
	}

	if (child_doctype === "PP EXPORT NON STOCK Items") {
		if (gsm === "22 GSM BLUE SURPLUS")return 0.17;
		// if (gsm === "22 GSM BLUE ARA") return 0.17;
		if ([
			"20 GSM GREY",
			"22 GSM BLACK",
			"22 GSM BLUE/2915",
			"22 GSM LIGHT BLUE",
			"45 GSM CANVAS"
		].includes(gsm)) return 0.23;
	}

	return 0.65;
}

function normalise_feet(value) {
	const feet = String(value || "").toUpperCase().replace("FEET", "").replace("FT", "").replaceAll(" ", "").trim();
	return { "6.0": "6", "7.50": "7.5", "75": "7.5", "8.30": "8.3", "83": "8.3", "10.0": "10", "11.0": "11", "12.0": "12" }[feet] || feet;
}

// *******************************************POND FABRIC STOCK Items calc*****************************************************
function update_total(frm) {
	let total_6 = 0;
	let total_10 = 0;
	let total_11 = 0;
	let total_12 = 0;
	let total_kg = 0;
	let total_fg_op = 0;

	(frm.doc.fabric_stock_items || []).forEach(row => {
		total_6 += flt(row["6ft_kg"]);
		total_10 += flt(row["10_ft_kg"]);
		total_11 += flt(row["11_ft_kg"]);
		total_12 += flt(row["12_ft_kg"]);
		total_kg += flt(row["totalkg"]);
		total_fg_op += flt(row["f_goutput_kg"]);
	});

	frm.set_value("total_6ft_kg", total_6);
	frm.set_value("total_10_ft_kg", total_10);
	frm.set_value("total_11_ft_kg", total_11);
	frm.set_value("total_12_ft_kg", total_12);
	frm.set_value("totalkg", total_kg);
	frm.set_value("total_fgoutput_kg", total_fg_op);

	update_grand_total_fgoutput(frm);

}

// *******************************************UNLAM SULZER FABRIC Items calc*****************************************************

function update_total_2(frm) {
	let total_6 = 0;
	let total_10 = 0;
	let total_12 = 0;
	let total_kg = 0;
	let total_fg_op = 0;

	(frm.doc.unlam_sulzer_fabric_items || []).forEach(row => {
		total_6 += flt(row["6ft_kg"]);
		total_10 += flt(row["10_ft_kg"]);
		total_12 += flt(row["12_ft_kg"]);
		total_kg += flt(row["totalkg"]);
		total_fg_op += flt(row["f_goutput_kg"]);
	});

	frm.set_value("total_6ft_kg_2", total_6);
	frm.set_value("total_10_ft_kg_2", total_10);
	frm.set_value("total_12_ft_kg_2", total_12);
	frm.set_value("totalkg_2", total_kg);
	frm.set_value("total_fgoutput_kg_2", total_fg_op);

	update_grand_total_fgoutput(frm);

}

// ******************************************UNLAM OTHER POND FABRIC Items calc*****************************************************
function update_total_3(frm) {
	let total_6 = 0;
	let total_10 = 0;
	let total_11 = 0;
	let total_12 = 0;
	let total_kg = 0;
	let total_fg_op = 0;

	(frm.doc.unlam__other_pond_fabric_items || []).forEach(row => {
		total_6 += flt(row["6ft_kg"]);
		total_10 += flt(row["10_ft_kg"]);
		total_11 += flt(row["11_ft_kg"]);
		total_12 += flt(row["12_ft_kg"]);
		total_kg += flt(row["totalkg"]);
		total_fg_op += flt(row["f_goutput_kg"]);
	});

	frm.set_value("total_6ft_kg_3", total_6);
	frm.set_value("total_10_ft_kg_3", total_10);
	frm.set_value("total_11_ft_kg_3", total_11);
	frm.set_value("total_12_ft_kg_3", total_12);
	frm.set_value("totalkg_3", total_kg);
	frm.set_value("total_fgoutput_kg_3", total_fg_op);

	update_grand_total_fgoutput(frm);

}

// ******************************************UNLAM PIPE STOCK Items calc*****************************************************
function update_total_4(frm) {
	let total_6 = 0;
	let total_10 = 0;
	let total_11 = 0;
	let total_12 = 0;
	let total_kg = 0;
	let total_fg_op = 0;

	(frm.doc.unlam_pipe_stock_items || []).forEach(row => {
		total_6 += flt(row["6ft_kg"]);
		total_10 += flt(row["83_ft_kg"]);
		total_11 += flt(row["75_ft_kg"]);
		total_kg += flt(row["totalkg"]);
		total_fg_op += flt(row["f_goutput_kg"]);
	});

	frm.set_value("total_6ft_kg_4", total_6);
	frm.set_value("total_83_ft_kg_4", total_10);
	frm.set_value("total_75_ft_kg_4", total_11);
	frm.set_value("totalkg_4", total_kg);
	frm.set_value("total_fgoutput_kg_4", total_fg_op);

	update_grand_total_fgoutput(frm);

}

// *************************************************UNLAM OTHER POND FABRIC Items calc********************************************
function update_total_5(frm) {
	let total_12 = 0;
	let total_83_ft = 0;
	let total_kg = 0;
	let total_fg_op = 0;

	(frm.doc.pp_export_unlam__fab_stock_items || []).forEach(row => {
		total_12 += flt(row["12_ft"]);
		total_83_ft += flt(row["83_ft"]);
		total_kg += flt(row["totalkg"]);
		total_fg_op += flt(row["f_g_outputkg"]);
	});

	frm.set_value("total_12_ft_kg_5", total_12);
	frm.set_value("total_83_ft_5", total_83_ft);
	frm.set_value("totalkg_5", total_kg);
	frm.set_value("total_fgoutput_kg_5", total_fg_op);

	update_grand_total_fgoutput(frm);

}

// ******************************************PP EXPORT NON STOCK Items calc********************************************
function update_total_6(frm) {
	let total_qty_kg = 0;
	let total_kg = 0;
	let total_fg_op = 0;

	(frm.doc.pp_export_non_stock_items || []).forEach(row => {
		total_qty_kg += flt(row["qty_kg"]);
		total_kg += flt(row["total_kg"]);
		total_fg_op += flt(row["fg__output_kg"]);
	});

	frm.set_value("total_qty_kg_6", total_qty_kg);
	frm.set_value("totalkg_6", total_kg);
	frm.set_value("total_fgoutput_kg_6", total_fg_op);

	update_grand_total_fgoutput(frm);

}
// ************************************CALC update_grand_total_fgoutput***********************************
function update_grand_total_fgoutput(frm) {
	const grand_total =
		flt(frm.doc.total_fgoutput_kg) +
		flt(frm.doc.total_fgoutput_kg_2) +
		flt(frm.doc.total_fgoutput_kg_3) +
		flt(frm.doc.total_fgoutput_kg_4) +
		flt(frm.doc.total_fgoutput_kg_5) +
		flt(frm.doc.total_fgoutput_kg_6);

	frm.set_value("grand_total_fgoutput_kg", grand_total);
}