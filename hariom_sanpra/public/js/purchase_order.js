frappe.ui.form.on("Purchase Order", {
    onload: function(frm) {
        // Only for new Purchase Orders
        if (!frm.is_new()) return;

        frappe.db.get_value(
            "Employee",
            { user_id: frappe.session.user },
            ["department"],
            function(r) {
                if (r && r.department === "Maintains - OM") {
                    frm.set_value("set_warehouse", "Maintenance - OM");
                }
            }
        );
    }
});  