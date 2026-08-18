frappe.pages["production_material_dashboard"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Production Material Dashboard"),
		single_column: true,
	});
	const dashboard = new ProductionMaterialDashboard(page);
	dashboard.render();
	dashboard.refresh();
	page.set_primary_action(__("Refresh"), () => dashboard.refresh(), "refresh");
};

class ProductionMaterialDashboard {
	constructor(page) { this.page = page; this.$main = $(page.main); }
	render() {
		this.add_styles();
		this.$main.html(`<div class="production-material-dashboard"><div class="pmd-grid"></div></div>`);
		this.render_loading();
	}
	add_styles() {
		if (document.getElementById("production-material-dashboard-styles")) return;
		$("<style>", { id: "production-material-dashboard-styles" }).text(`
			.production-material-dashboard { padding: 8px 0 24px; }
			.pmd-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 30px; }
			.pmd-card { min-height: 276px; padding: 36px 40px 34px; border: 1px solid #e3e5e8; border-radius: 24px; background: #fff; box-shadow: 0 1px 2px rgba(17, 24, 39, .02); }
			.pmd-title { display: flex; align-items: center; gap: 18px; margin-bottom: 30px; color: #111; font-size: 30px; font-weight: 700; line-height: 1.2; }
			.pmd-icon { display: inline-flex; width: 34px; height: 34px; color: #245c96; }
			.pmd-icon svg { width: 100%; height: 100%; }
			.pmd-values { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; }
			.pmd-value { min-height: 112px; padding: 23px 24px; border-radius: 16px; background: #fafafa; }
			.pmd-value.status-danger { background: #f8d2d2; }
			.pmd-value.status-danger .pmd-label, .pmd-value.status-danger .pmd-qty { color: #8d2424; }
			.pmd-value.status-warning { background: #ffe2a6; }
			.pmd-value.status-warning .pmd-label, .pmd-value.status-warning .pmd-qty { color: #765000; }
			.pmd-value.status-safe { background: #cceaca; }
			.pmd-value.status-safe .pmd-label, .pmd-value.status-safe .pmd-qty { color: #087514; }
			.pmd-label { margin-bottom: 4px; color: #555; font-size: 21px; line-height: 1.25; }
			.pmd-qty { color: #111; font-size: 29px; font-weight: 600; line-height: 1.25; }
			.pmd-wastage { margin-top: 22px; color: #888; font-size: 20px; line-height: 1.4; }
			.pmd-loading { min-height: 260px; display: grid; place-items: center; color: #777; }
			@media (max-width: 900px) { .pmd-grid { grid-template-columns: 1fr; gap: 20px; } }
			@media (max-width: 520px) { .pmd-card { min-height: auto; padding: 26px 22px; border-radius: 18px; } .pmd-title { font-size: 25px; } .pmd-values { grid-template-columns: 1fr; } }
		`).appendTo("head");
	}
	render_loading() { this.$main.find(".pmd-grid").html(`<div class="pmd-loading">${__("Loading stock balances...")}</div>`); }
	async refresh() {
		this.render_loading();
		try {
			const response = await frappe.call({ method: "hariom_sanpra.hariom_sanpra.page.production_material_dashboard.production_material_dashboard.get_dashboard_data" });
			this.render_cards(response.message || []);
		} catch (error) {
			this.$main.find(".pmd-grid").empty();
			frappe.msgprint({ title: __("Unable to load dashboard"), message: __("Stock balances could not be fetched. Please try again."), indicator: "red" });
		}
	}
	render_cards(products) {
		const cards = products.map((product) => `
			<section class="pmd-card">
				<div class="pmd-title">${this.get_icon(product.icon)}<span>${frappe.utils.escape_html(product.label)}</span></div>
				<div class="pmd-values">
					${this.raw_material_block(product.raw_material_days)}
					${this.value_block(__("Semi-ready"), product.semi_ready)}
					${this.value_block(__("Ready stock"), product.ready_stock)}
				</div>
				<div class="pmd-wastage">${__("Wastage this month: {0}%", [format_number(product.wastage_percent || 0, null, 2)])}</div>
			</section>`);
		this.$main.find(".pmd-grid").html(cards.join(""));
	}
	raw_material_block(days_left) {
		if (days_left === null || days_left === undefined) {
			return `<div class="pmd-value"><div class="pmd-label">${__("Raw material")}</div><div class="pmd-qty">—</div></div>`;
		}
		const whole_days = Math.max(0, Math.floor(days_left));
		const status = whole_days <= 3 ? "danger" : whole_days <= 10 ? "warning" : "safe";
		return `<div class="pmd-value status-${status}"><div class="pmd-label">${__("Raw material")}</div><div class="pmd-qty">${__("{0} days left", [whole_days])}</div></div>`;
	}
	value_block(label, value) {
		const quantity = value === null ? "—" : `${format_number(value, null, 3)} ${__("ton")}`;
		return `<div class="pmd-value"><div class="pmd-label">${label}</div><div class="pmd-qty">${quantity}</div></div>`;
	}
	get_icon(icon) {
		const icons = {
			drop: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2.5S5.5 9.7 5.5 14.5a6.5 6.5 0 0 0 13 0C18.5 9.7 12 2.5 12 2.5Z"/></svg>',
			pipe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 7h10a4 4 0 0 1 4 4v6"/><path d="M5 4v6M2 5.5h3M2 8.5h3M16 17h6M17.5 20v-3M20.5 20v-3"/></svg>',
			box: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 2.5 8 4.3v10.4l-8 4.3-8-4.3V6.8L12 2.5Z"/><path d="m4 6.8 8 4.5 8-4.5M12 11.3v10.2M8 4.7l8 4.4"/></svg>',
			layers: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="7" y="4" width="12" height="12" rx="3"/><rect x="3" y="8" width="12" height="12" rx="3"/></svg>',
		};
		return `<span class="pmd-icon">${icons[icon] || icons.box}</span>`;
	}
}
