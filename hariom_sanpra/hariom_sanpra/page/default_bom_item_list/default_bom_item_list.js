frappe.pages["default-bom-item-list"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Default BOM Item List"),
		single_column: true,
	});

	new hariom_sanpra.DefaultBOMItemList(page);
};

frappe.provide("hariom_sanpra");

hariom_sanpra.DefaultBOMItemList = class DefaultBOMItemList {
	constructor(page) {
		this.page = page;
		this.start = 0;
		this.page_length = 50;
		this.items = [];
		this.item_boms = {};
		this.bom_details = {};
		this.make();
		this.load_items();
	}

	make() {
		this.page.set_primary_action(__("Refresh"), () => this.load_items(), "refresh");
		this.$body = $(`
			<div class="default-bom-item-list">
				<style>
					.default-bom-item-list .table {
						font-size: 12px;
					}
					.default-bom-item-list .table th,
					.default-bom-item-list .table td {
						padding: 6px 8px;
						vertical-align: middle;
					}
					.default-bom-item-list .default-bom-link {
						color: #1f6feb;
						font-weight: 600;
					}
					.default-bom-item-list .nested-table {
						margin-bottom: 8px;
					}
					.default-bom-item-list .toggle-label {
						display: inline-block;
						min-width: 10px;
					}
				</style>
				<div class="frappe-control input-max-width margin-bottom">
					<input class="form-control item-search" type="text" placeholder="${__("Search Item")}">
				</div>
				<div class="result"></div>
			</div>
		`).appendTo(this.page.body);

		this.$result = this.$body.find(".result");
		this.$body.find(".item-search").on(
			"input",
			frappe.utils.debounce(() => {
				this.start = 0;
				this.load_items();
			}, 300)
		);
	}

	load_items() {
		this.$result.html(`<div class="text-muted">${__("Loading...")}</div>`);
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.page.default_bom_item_list.default_bom_item_list.get_items",
			args: {
				start: this.start,
				page_length: this.page_length,
				item_code: this.$body.find(".item-search").val(),
			},
			callback: (r) => {
				this.items = r.message || [];
				this.render_items();
			},
		});
	}

	render_items() {
		if (!this.items.length) {
			this.$result.html(`<div class="text-muted">${__("No items found with Default BOM.")}</div>`);
			return;
		}

		const rows = this.items
			.map((item) => {
				const item_code = frappe.utils.escape_html(item.item_code || item.name);
				const item_name = frappe.utils.escape_html(item.item_name || "");
				const default_bom = frappe.utils.escape_html(item.default_bom || "");
				const stock_uom = frappe.utils.escape_html(item.stock_uom || "");
				const item_route = encodeURIComponent(item.item_code || item.name);
				const bom_route = encodeURIComponent(item.default_bom || "");

				return `
					<tr class="item-row" data-item="${item_code}" data-bom="${default_bom}">
						<td class="text-center" style="width: 48px;">
							<button class="btn btn-xs btn-default expand-item" title="${__("Show BOM Items")}">
								<span class="toggle-label">&gt;</span>
							</button>
						</td>
						<td><a href="/app/item/${item_route}">${item_code}</a></td>
						<td>${item_name}</td>
						<td>${stock_uom}</td>
						<td><a href="/app/bom/${bom_route}">${default_bom}</a></td>
					</tr>
					<tr class="bom-detail-row hidden" data-parent-item="${item_code}">
						<td></td>
						<td colspan="4" class="bom-list-cell"></td>
					</tr>
				`;
			})
			.join("");

		this.$result.html(`
			<table class="table table-bordered">
				<thead>
					<tr>
						<th></th>
						<th>${__("Item Code")}</th>
						<th>${__("Item Name")}</th>
						<th>${__("Stock UOM")}</th>
						<th>${__("Default BOM")}</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		`);

		this.$result.find(".expand-item").on("click", (event) => {
			const $row = $(event.currentTarget).closest(".item-row");
			this.toggle_item_boms($row);
		});
	}

	toggle_item_boms($row) {
		const item = $row.data("item");
		const $detail = this.$result
			.find(".bom-detail-row")
			.filter((index, row) => $(row).data("parent-item") === item);
		const $button_label = $row.find(".expand-item .toggle-label");

		if (!$detail.hasClass("hidden")) {
			$detail.addClass("hidden");
			$button_label.html("&gt;");
			return;
		}

		$detail.removeClass("hidden");
		$button_label.text("v");

		if (this.item_boms[item]) {
			$detail.find(".bom-list-cell").html(this.get_bom_list_html(item, this.item_boms[item]));
			this.bind_bom_row_events($detail);
			this.bind_create_buttons($detail);
			return;
		}

		$detail.find(".bom-list-cell").html(`<div class="text-muted">${__("Loading BOMs...")}</div>`);
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.page.default_bom_item_list.default_bom_item_list.get_boms",
			args: { item_code: item },
			callback: (r) => {
				this.item_boms[item] = r.message || [];
				$detail.find(".bom-list-cell").html(this.get_bom_list_html(item, this.item_boms[item]));
				this.bind_bom_row_events($detail);
				this.bind_create_buttons($detail);
			},
		});
	}

	get_bom_list_html(item, boms) {
		if (!boms.length) {
			return `<div class="text-muted">${__("No BOM found for this item.")}</div>`;
		}

		const rows = boms
			.map((bom) => {
				const bom_no = frappe.utils.escape_html(bom.name || "");
				const bom_route = encodeURIComponent(bom.name || "");
				const qty = frappe.format(bom.quantity || 0, { fieldtype: "Float" });
				const uom = frappe.utils.escape_html(bom.uom || "");
				const company = frappe.utils.escape_html(bom.company || "");
				const default_class = bom.is_default ? "default-bom-link" : "";
				const active_label = bom.is_active ? __("Yes") : __("No");
				const default_label = bom.is_default ? __("Yes") : __("No");
				const create_disabled = bom.docstatus !== 1 || !bom.is_active || bom.is_phantom_bom ? "disabled" : "";
				const button_title = create_disabled
					? __("Work Order can be created only for active submitted non-phantom BOM.")
					: __("Create Work Order");

				return `
					<tr class="bom-row" data-bom="${bom_no}">
						<td class="text-center" style="width: 42px;">
							<button class="btn btn-xs btn-default expand-bom" title="${__("Show BOM Details")}">
								<span class="toggle-label">&gt;</span>
							</button>
						</td>
						<td><a class="${default_class}" href="/app/bom/${bom_route}">${bom_no}</a></td>
						<td class="text-right">${qty}</td>
						<td>${uom}</td>
						<td>${company}</td>
						<td class="text-center">${bom.docstatus === 1 ? __("Submitted") : __("Draft")}</td>
						<td class="text-center">${active_label}</td>
						<td class="text-center ${bom.is_default ? "default-bom-link" : ""}">${default_label}</td>
						<td class="text-right">
							<button class="btn btn-primary btn-xs create-work-order" data-bom="${bom_no}" data-item="${frappe.utils.escape_html(item)}" data-company="${company}" ${create_disabled} title="${button_title}">
								${__("Create Work Order")}
							</button>
						</td>
					</tr>
					<tr class="bom-items-row hidden" data-parent-bom="${bom_no}">
						<td></td>
						<td colspan="8" class="bom-items-cell"></td>
					</tr>
				`;
			})
			.join("");

		return `
			<table class="table table-bordered table-condensed nested-table">
				<thead>
					<tr>
						<th></th>
						<th>${__("BOM")}</th>
						<th class="text-right">${__("Qty")}</th>
						<th>${__("UOM")}</th>
						<th>${__("Company")}</th>
						<th class="text-center">${__("Docstatus")}</th>
						<th class="text-center">${__("Active")}</th>
						<th class="text-center">${__("Default")}</th>
						<th class="text-right">${__("Action")}</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		`;
	}

	bind_bom_row_events($detail) {
		$detail.find(".expand-bom").on("click", (event) => {
			const $row = $(event.currentTarget).closest(".bom-row");
			this.toggle_bom_items($row);
		});
	}

	toggle_bom_items($row) {
		const bom_no = $row.data("bom");
		const $detail = this.$result
			.find(".bom-items-row")
			.filter((index, row) => $(row).data("parent-bom") === bom_no);
		const $button_label = $row.find(".expand-bom .toggle-label");

		if (!$detail.hasClass("hidden")) {
			$detail.addClass("hidden");
			$button_label.html("&gt;");
			return;
		}

		$detail.removeClass("hidden");
		$button_label.text("v");

		if (this.bom_details[bom_no]) {
			$detail.find(".bom-items-cell").html(this.get_bom_items_html(this.bom_details[bom_no]));
			return;
		}

		$detail.find(".bom-items-cell").html(`<div class="text-muted">${__("Loading BOM details...")}</div>`);
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.page.default_bom_item_list.default_bom_item_list.get_bom_items",
			args: { bom_no },
			callback: (r) => {
				this.bom_details[bom_no] = r.message || {};
				$detail.find(".bom-items-cell").html(this.get_bom_items_html(this.bom_details[bom_no]));
			},
		});
	}

	get_bom_items_html(data) {
		const bom = data.bom || {};
		const items = data.items || [];

		const rows = items.length
			? items
					.map((row) => {
						const item_code = frappe.utils.escape_html(row.item_code || "");
						const item_name = frappe.utils.escape_html(row.item_name || "");
						const qty = frappe.format(row.qty || 0, { fieldtype: "Float" });
						const uom = frappe.utils.escape_html(row.uom || "");
						const bom_no = frappe.utils.escape_html(row.bom_no || "");
						const item_route = encodeURIComponent(row.item_code || "");
						const bom_route = encodeURIComponent(row.bom_no || "");

						return `
							<tr>
								<td>${row.idx || ""}</td>
								<td><a href="/app/item/${item_route}">${item_code}</a></td>
								<td>${item_name}</td>
								<td class="text-right">${qty}</td>
								<td>${uom}</td>
								<td>${bom_no ? `<a href="/app/bom/${bom_route}">${bom_no}</a>` : ""}</td>
							</tr>
						`;
					})
					.join("")
			: `<tr><td colspan="6" class="text-muted">${__("No BOM items found.")}</td></tr>`;

		return `
			<div class="margin-bottom">
				<div>
					<strong>${__("BOM")}:</strong>
					<a href="/app/bom/${encodeURIComponent(bom.name || "")}">${frappe.utils.escape_html(bom.name || "")}</a>
					<span class="text-muted">(${__("Qty")}: ${frappe.format(bom.quantity || 0, { fieldtype: "Float" })} ${frappe.utils.escape_html(bom.uom || "")})</span>
				</div>
			</div>
			<table class="table table-bordered table-condensed">
				<thead>
					<tr>
						<th style="width: 60px;">${__("No.")}</th>
						<th>${__("BOM Item")}</th>
						<th>${__("Item Name")}</th>
						<th class="text-right">${__("Qty")}</th>
						<th>${__("UOM")}</th>
						<th>${__("Sub BOM")}</th>
					</tr>
				</thead>
				<tbody>${rows}</tbody>
			</table>
		`;
	}

	bind_create_buttons($detail) {
		$detail.find(".create-work-order").on("click", (event) => {
			const $button = $(event.currentTarget);
			this.show_work_order_dialog({
				bom_no: $button.data("bom"),
				item: $button.data("item"),
				company: $button.data("company"),
			});
		});
	}

	show_work_order_dialog(args) {
		const dialog = new frappe.ui.Dialog({
			title: __("Create Work Order"),
			fields: [
				{
					fieldname: "qty",
					fieldtype: "Float",
					label: __("Qty"),
					reqd: 1,
					default: 1,
				},
				{
					fieldname: "use_multi_level_bom",
					fieldtype: "Check",
					label: __("Use Multi-Level BOM"),
					default: 0,
				},
			],
			primary_action_label: __("Create"),
			primary_action: (values) => {
				dialog.hide();
				this.create_work_order({
					...args,
					qty: values.qty,
					use_multi_level_bom: values.use_multi_level_bom ? 1 : 0,
				});
			},
		});

		dialog.show();
	}

	create_work_order(args) {
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.page.default_bom_item_list.default_bom_item_list.make_work_order",
			args,
			freeze: true,
			callback: (r) => {
				if (r.message) {
					const doc = frappe.model.sync(r.message)[0];
					frappe.set_route("Form", doc.doctype, doc.name);
				}
			},
		});
	}
};
