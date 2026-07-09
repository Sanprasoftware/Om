
frappe.ui.form.on("Item", {
	refresh(frm) {
		toggle_has_batch_field(frm);
		frm.set_query("custom_batch", function () {
			return {
				filters: {
					item: frm.doc.name
				}
			};
		});
	},
	item_group(frm) {
        toggle_has_batch_field(frm);
    }
});


function toggle_has_batch_field(frm) {
    if (!frm.doc.item_group) {
        frm.set_df_property("has_batch_no", "read_only", 0);
        frm.set_df_property("has_serial_no", "read_only", 0);
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Item Group",
            name: frm.doc.item_group
        },
        callback(r) {
            if (r.message) {
                check_parent(frm, r.message);
            }
        }
    });
}

function check_parent(frm, group) {
    if (group.name === "Maintainance") {
        frm.set_value("has_batch_no", 0);
        frm.set_df_property("has_batch_no", "read_only", 1);
        frm.set_df_property("has_serial_no", "read_only", 1);
        return;
    }

    if (!group.parent_item_group) {
        frm.set_df_property("has_batch_no", "read_only", 0);
        frm.set_df_property("has_serial_no", "read_only", 0);
        return;
    }

    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Item Group",
            name: group.parent_item_group
        },
        callback(r) {
            if (r.message) {
                check_parent(frm, r.message);
            }
        }
    });
}