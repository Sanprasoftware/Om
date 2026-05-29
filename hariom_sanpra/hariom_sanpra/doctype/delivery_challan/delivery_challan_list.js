frappe.listview_settings["delivery challan"] = {
	add_fields: ["type", "status", "docstatus"],
	get_indicator(doc) {
		if (doc.type === "OUT" && doc.status) {
			const colors = {
				Pending: "orange",
				Partially: "orange",
				Completed: "green"
			};

			return [__(doc.status), colors[doc.status] || "gray", `status,=,${doc.status}`];
		}

		if (doc.docstatus === 0) {
			return [__("Draft"), "red", "docstatus,=,0"];
		}

		if (doc.docstatus === 1) {
			return [__("Submitted"), "blue", "docstatus,=,1"];
		}

		return [__("Cancelled"), "red", "docstatus,=,2"];
	}
};
