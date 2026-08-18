app_name = "hariom_sanpra"
app_title = "Hariom Sanpra"
app_publisher = "Sanpra Software Solution"
app_description = "Hariom Sanpra"
app_email = "sanprasoftwares@gmail.com"
app_license = "mit"

# Apps
# ------------------ 

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "hariom_sanpra",
# 		"logo": "/assets/hariom_sanpra/logo.png",
# 		"title": "Hariom Sanpra",
# 		"route": "/hariom_sanpra",
# 		"has_permission": "hariom_sanpra.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/hariom_sanpra/css/hariom_sanpra.css"
# app_include_js = "/assets/hariom_sanpra/js/hariom_sanpra.js"


# include js, css files in header of web template
# web_include_css = "/assets/hariom_sanpra/css/hariom_sanpra.css"
# web_include_js = "/assets/hariom_sanpra/js/hariom_sanpra.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "hariom_sanpra/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
doctype_js = {
	"Stock Entry": "public/js/stock_entry.js",
	"Work Order": "public/js/work_order.js",
	"Delivery Note": "public/js/delivery_note.js",
	"Item": "public/js/item.js",
	"Purchase Order": "public/js/purchase_order.js",
	"Purchase Receipt": "public/js/purchase_receipt.js",
	"Quality Inspection": "public/js/quality_inspection.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "hariom_sanpra/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "hariom_sanpra.utils.jinja_methods",
# 	"filters": "hariom_sanpra.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "hariom_sanpra.install.before_install"
# after_install = "hariom_sanpra.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "hariom_sanpra.uninstall.before_uninstall"
# after_uninstall = "hariom_sanpra.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "hariom_sanpra.utils.before_app_install"
# after_app_install = "hariom_sanpra.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "hariom_sanpra.utils.before_app_uninstall"
# after_app_uninstall = "hariom_sanpra.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "hariom_sanpra.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	# "Item": {
	# 	"before_save": "hariom_sanpra.public.py.item.create_new_item"
	# },
	"Delivery Note": {
		"on_submit": "hariom_sanpra.public.py.delivery_note.create_stock_entry"
	},
	"Stock Entry": {
		"before_save": "hariom_sanpra.public.py.stock_entry.get_finished_qty",
        "on_submit": "hariom_sanpra.public.py.stock_entry.set_job_name"
	# 	"before_save": "hariom_sanpra.public.py.stock_entry.calculation",
	# 	"before_insert": "hariom_sanpra.public.py.stock_entry.set_batch"
	},
	# "Navrang Rewinding Machine": {
	# 	"on_submit": "hariom_sanpra.hariom_sanpra.doctype.navrang_rewinding_machine.navrang_rewinding_machine.create_stock_entry"
	# },
	"BOM": {
		"on_update_after_submit": "hariom_sanpra.public.py.bom.set_bom"
	},
    "Quality Inspection": {
        "on_update": "hariom_sanpra.public.py.quality_inspection.update_reference_qc_status",
        "on_submit": "hariom_sanpra.public.py.quality_inspection.update_reference_qc_status",
        "on_cancel": "hariom_sanpra.public.py.quality_inspection.update_reference_qc_status",
        "before_save": "hariom_sanpra.public.py.quality_inspection.set_readings_status",
    },
    "ToDo": {
        "after_insert": "hariom_sanpra.public.py.todo.notify_assigned_user"
    }

}
# /home/hariom/bench-uat/apps/hariom_sanpra/hariom_sanpra/hariom_sanpra.doctype.navrang_rewinding_machine.navrang_rewinding_machine.py
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"hariom_sanpra.tasks.all"
# 	],
# 	"daily": [
# 		"hariom_sanpra.tasks.daily"
# 	],
# 	"hourly": [
# 		"hariom_sanpra.tasks.hourly"
# 	],
# 	"weekly": [
# 		"hariom_sanpra.tasks.weekly"
# 	],
# 	"monthly": [
# 		"hariom_sanpra.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "hariom_sanpra.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
extend_doctype_class = {
	"Work Order": "hariom_sanpra.overrides.work_order.WorkOrderTimeLogMixin"
}

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "hariom_sanpra.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "hariom_sanpra.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["hariom_sanpra.utils.before_request"]
# after_request = ["hariom_sanpra.utils.after_request"]

# Job Events
# ----------
# before_job = ["hariom_sanpra.utils.before_job"]
# after_job = ["hariom_sanpra.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"hariom_sanpra.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []


