frappe.pages["hariom-material-alert"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Hariom Material Alert"),
		single_column: true,
	});

	new hariom_sanpra.MaterialAlert(page);
};

frappe.provide("hariom_sanpra");

hariom_sanpra.MaterialAlert = class MaterialAlert {
	constructor(page) {
		this.page = page;
		this.make_filter();
		this.make_body();
		this.page.set_primary_action(__("Refresh"), () => this.load(), "refresh");
		this.load();
	}

	make_filter() {
		this.company = this.page.add_field({
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_default("company"),
			change: () => {
				this.warehouse.set_value("");
				this.load();
			},
		});

		this.warehouse = this.page.add_field({
			fieldname: "warehouse",
			label: __("Warehouse"),
			fieldtype: "Link",
			options: "Warehouse",
			get_query: () => ({
				filters: {
					company: this.company.get_value(),
					disabled: 0,
				},
			}),
			change: () => this.load(),
		});

		this.item_group = this.page.add_field({
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group",
			default: "Raw Material",
			get_query: () => ({
				query: "hariom_sanpra.hariom_sanpra.page.hariom_material_alert.hariom_material_alert.get_raw_material_item_groups",
			}),
			change: () => this.load(),
		});
	}

	make_body() {
		this.$body = $(`
			<div class="material-alert-dashboard">
				<style>
					.material-alert-dashboard { padding: 8px 0 24px; }
					.material-alert-grid {
						display: grid;
						grid-template-columns: repeat(4, minmax(0, 1fr));
						gap: 28px;
					}
					.material-alert-card {
						position: relative;
						min-height: 178px;
						padding: 30px 36px;
						background: var(--card-bg, #fff);
						border: 1px solid var(--border-color, #e2e2e2);
						border-radius: 24px;
						box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
					}
					.material-alert-title { font-size: 19px; font-weight: 600; line-height: 1.25; padding-right: 30px; }
					.material-alert-qty { margin-top: 22px; font-size: 27px; font-weight: 700; line-height: 1; }
					.material-alert-days { margin-top: 10px; font-size: 15px; line-height: 1.25; }
					.material-alert-dot { position: absolute; top: 34px; right: 34px; width: 18px; height: 18px; border-radius: 50%; }
					.status-safe .material-alert-dot { background: #08a317; }
					.status-safe .material-alert-days { color: #087514; }
					.status-warning .material-alert-dot { background: #ffb21a; }
					.status-warning .material-alert-days { color: #765000; }
					.status-danger .material-alert-dot { background: #dc3d3d; }
					.status-danger .material-alert-days { color: #8b1d1d; }
					@media (max-width: 991px) { .material-alert-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; } }
					@media (max-width: 600px) { .material-alert-grid { grid-template-columns: 1fr; gap: 16px; } .material-alert-card { min-height: 155px; padding: 25px 28px; } }
				</style>
				<div class="material-alert-result"></div>
			</div>
		`).appendTo(this.page.body);
		this.$result = this.$body.find(".material-alert-result");
	}

	load() {
		this.$result.html(`<div class="text-muted">${__("Loading stock...")}</div>`);
		frappe.call({
			method: "hariom_sanpra.hariom_sanpra.page.hariom_material_alert.hariom_material_alert.get_material_stock",
			args: {
				company: this.company.get_value(),
				warehouse: this.warehouse.get_value(),
				item_group: this.item_group.get_value() || "Raw Material",
				consumption_days: 30,
			},
			callback: (r) => this.render(r.message || []),
		});
	}

	render(rows) {
		if (!rows.length) {
			this.$result.html(`<div class="text-muted">${__("No stock found for the selected filters.")}</div>`);
			return;
		}

		const cards = rows.map((row) => {
			const title = frappe.utils.escape_html(row.item_group || __("Unassigned"));
			const uom = frappe.utils.escape_html(row.stock_uom || "");
			const qty = format_number(row.actual_qty, null, 2);
			let days_text = __("No recent consumption");
			if (row.days_left !== null && row.days_left !== undefined) {
				const days = Math.max(0, Math.floor(row.days_left));
				days_text = row.status === "danger"
					? __("{0} day(s) left · order now", [days])
					: __("{0} day(s) left", [days]);
			}

			return `
				<div class="material-alert-card status-${row.status || "safe"}">
					<span class="material-alert-dot" aria-hidden="true"></span>
					<div class="material-alert-title">${title}</div>
					<div class="material-alert-qty">${qty} ${uom}</div>
					<div class="material-alert-days">${days_text}</div>
				</div>`;
		}).join("");

		this.$result.html(`<div class="material-alert-grid">${cards}</div>`);
	}
};
