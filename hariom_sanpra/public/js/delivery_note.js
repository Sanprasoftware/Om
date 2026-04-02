frappe.ui.form.on('Packing Material', {
	item_code: function(frm, cdt, cdn) {
        get_stock(frm, cdt, cdn);
    },
    warehouse: function(frm, cdt, cdn) {
        get_stock(frm, cdt, cdn);
    }
})

function get_stock(frm, cdt, cdn){
    let row = locals[cdt][cdn];

    if (row.item_code && row.warehouse){
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Bin",
                filters: {
                    item_code: row.item_code,
                    warehouse: row.warehouse
                },
                fieldname: ["actual_qty"]
            },
            callback: function(r){
                if (r.message){
                    frappe.model.set_value(cdt, cdn, "available_stock", r.message.actual_qty);
                } else {
                    frappe.model.set_value(cdt, cdn, "available_stock", 0);
                }
            }
        });
    }
}