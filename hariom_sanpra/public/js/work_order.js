frappe.ui.form.on("Work Order", {
	setup(frm) {
		frm.set_query("employee", "custom_job_card_time_log", () => {
			return {
				filters: {
					company: frm.doc.company,
					status: "Active",
				},
			};
		});
	},

	refresh(frm) {
		stop_job_timer(frm);

		if (frm.is_new() || frm.doc.docstatus !== 1) {
			return;
		}

		const summary = get_job_log_summary(frm.doc);

		if (summary.in_progress) {
			add_pause_button(frm);
			add_complete_button(frm, true);
			start_job_timer(frm, summary.open_since);
			return;
		}

		if (summary.is_completed) {
			return;
		}

		if (summary.is_paused) {
			add_resume_button(frm, summary.employees);
			add_complete_button(frm, false);
			return;
		}

		add_start_button(frm);
	},
});

function add_start_button(frm) {
	frm.add_custom_button(__("Start Job"), () => {
		prompt_for_employees(frm, __("Start Job"), (employees) => {
			call_work_order_job_method(frm, "start_job", {
				start_time: frappe.datetime.now_datetime(),
				employees,
			});
		});
	});
}

function add_pause_button(frm) {
	frm.add_custom_button(__("Pause Job"), () => {
		call_work_order_job_method(frm, "pause_job", {
			end_time: frappe.datetime.now_datetime(),
		});
	});
}

function add_resume_button(frm, employees) {
	frm.add_custom_button(__("Resume Job"), () => {
		const resume = (selected_employees) => {
			call_work_order_job_method(frm, "resume_job", {
				start_time: frappe.datetime.now_datetime(),
				employees: selected_employees,
			});
		};

		if (employees?.length) {
			resume(employees);
			return;
		}

		prompt_for_employees(frm, __("Resume Job"), resume);
	});
}

function add_complete_button(frm, include_end_time) {
	frm.add_custom_button(__("Complete Job"), () => {
		const fields = [
			{
				fieldtype: "Float",
				fieldname: "completed_qty",
				label: __("Completed Qty"),
				reqd: 1,
			},
		];

		if (include_end_time) {
			fields.push({
				fieldtype: "Datetime",
				fieldname: "end_time",
				label: __("End Time"),
				reqd: 1,
				default: frappe.datetime.now_datetime(),
			});
		}

		frappe.prompt(fields, (values) => {
			if (flt(values.completed_qty) <= 0) {
				frappe.throw(__("Completed Qty must be greater than 0."));
			}

			call_work_order_job_method(frm, "complete_job", values);
		}, __("Complete Job"), __("Update"));
	});
}

function prompt_for_employees(frm, title, callback) {
	frappe.prompt(
		[
			{
				fieldtype: "MultiSelectList",
				fieldname: "employees",
				label: __("Employees"),
				reqd: 1,
				get_data(txt) {
					return frappe.db.get_link_options("Employee", txt, {
						company: frm.doc.company,
						status: "Active",
					});
				},
			},
		],
		(values) => callback(values.employees || []),
		title,
		__("Start")
	);
}

function call_work_order_job_method(frm, method, args) {
	frm.call({
		method,
		doc: frm.doc,
		args,
		freeze: true,
		callback() {
			frm.reload_doc();
		},
	});
}

function get_job_log_summary(doc) {
	const time_logs = doc.custom_job_card_time_log || [];
	const open_logs = time_logs.filter((row) => row.from_time && !row.to_time);
	const last_log = time_logs[time_logs.length - 1];
	const target_qty = flt(doc.qty);
	const total_completed_qty = time_logs.reduce((total, row) => total + flt(row.completed_qty), 0);
	const employees = [...new Set(time_logs.map((row) => row.employee).filter(Boolean))];
	const openSince = open_logs.length
		? open_logs
				.map((row) => frappe.datetime.str_to_obj(row.from_time))
				.sort((left, right) => left - right)[0]
		: null;
	const is_completed = target_qty > 0 ? total_completed_qty >= target_qty : false;
	const is_paused = time_logs.length > 0 && !open_logs.length && !is_completed && !(last_log && flt(last_log.completed_qty) > 0);

	return {
		in_progress: open_logs.length > 0,
		is_paused,
		is_completed,
		employees,
		open_since: openSince,
	};
}

function start_job_timer(frm, startTime) {
	if (!startTime) {
		return;
	}

	if (!frm.job_timer_html) {
		frm.job_timer_html = $('<span class="job-timer" style="margin-left:15px;font-size:16px;font-weight:bold;"></span>');
		frm.page.wrapper.find(".page-actions").append(frm.job_timer_html);
	}

	const render = () => {
		const elapsedSeconds = Math.max(0, Math.floor((new Date() - startTime) / 1000));
		const hours = Math.floor(elapsedSeconds / 3600);
		const minutes = Math.floor((elapsedSeconds % 3600) / 60);
		const seconds = elapsedSeconds % 60;

		frm.job_timer_html.text(
			`${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`
		);
	};

	render();
	frm.job_timer_interval = setInterval(render, 1000);
}

function stop_job_timer(frm) {
	if (frm.job_timer_interval) {
		clearInterval(frm.job_timer_interval);
		frm.job_timer_interval = null;
	}

	if (frm.job_timer_html) {
		frm.job_timer_html.remove();
		frm.job_timer_html = null;
	}
}
