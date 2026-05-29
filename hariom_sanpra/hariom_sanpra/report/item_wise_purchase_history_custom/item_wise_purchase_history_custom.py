import frappe


def execute(filters=None):

	columns = get_columns()
	data = get_data(filters)

	return columns, data
def get_columns():

	columns = [

		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 140
		},

		{
			"label": "Item Group",
			"fieldname": "item_group",
			"fieldtype": "Data",
			"width": 180
		},

		{
			"label": "Item Name",
			"fieldname": "item_name",
			"fieldtype": "Data",
			"width": 220
		},

		{
			"label": "Description",
			"fieldname": "description",
			"fieldtype": "Small Text",
			"width": 250
		},

		{
			"label": "Qty",
			"fieldname": "qty",
			"fieldtype": "Float",
			"width": 100
		},

		{
			"label": "UOM",
			"fieldname": "uom",
			"fieldtype": "Data",
			"width": 100
		},

		{
			"label": "Rate",
			"fieldname": "rate",
			"fieldtype": "Currency",
			"width": 120
		},

		{
			"label": "Amount",
			"fieldname": "amount",
			"fieldtype": "Currency",
			"width": 120
		},

		{
			"label": "PO ID",
			"fieldname": "purchase_order",
			"fieldtype": "Link",
			"options": "Purchase Order",
			"width": 180
		},

		{
			"label": "Transaction Date",
			"fieldname": "transaction_date",
			"fieldtype": "Date",
			"width": 130
		},

		{
			"label": "Supplier",
			"fieldname": "supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"width": 180
		},

		{
			"label": "Supplier Name",
			"fieldname": "supplier_name",
			"fieldtype": "Data",
			"width": 220
		},

		{
			"label": "Supplier Group",
			"fieldname": "supplier_group",
			"fieldtype": "Data",
			"width": 180
		},

		{
			"label": "Project",
			"fieldname": "project",
			"fieldtype": "Link",
			"options": "Project",
			"width": 150
		},

		{
			"label": "Received Qty",
			"fieldname": "received_qty",
			"fieldtype": "Float",
			"width": 130
		},

		{
			"label": "Billed Amount",
			"fieldname": "billed_amt",
			"fieldtype": "Currency",
			"width": 140
		},

		{
			"label": "Company",
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 180
		}

	]

	return columns
def get_data(filters):

	conditions = ""
	values = {}

	# -----------------------------
	# DATE FILTER
	# -----------------------------

	if filters.get("from_date"):
		conditions += " AND po.transaction_date >= %(from_date)s"
		values["from_date"] = filters.get("from_date")

	if filters.get("to_date"):
		conditions += " AND po.transaction_date <= %(to_date)s"
		values["to_date"] = filters.get("to_date")

	# -----------------------------
	# COMPANY FILTER
	# -----------------------------

	if filters.get("company"):
		conditions += " AND po.company = %(company)s"
		values["company"] = filters.get("company")

	# -----------------------------
	#  ITEM FILTER
	# -----------------------------

	if filters.get("item_code"):
		conditions += " AND poi.item_code = %(item_code)s"
		values["item_code"] = filters.get("item_code")
	# -----------------------------
	# ITEM GROUP TREE FILTER
	# -----------------------------

	if filters.get("item_group"):

		item_group = frappe.db.get_value(
			"Item Group",
			filters.get("item_group"),
			["lft", "rgt"],
			as_dict=1
		)

		item_groups = frappe.get_all(
			"Item Group",
			filters={
				"lft": [">=", item_group.lft],
				"rgt": ["<=", item_group.rgt]
			},
			pluck="name"
		)

		conditions += " AND item.item_group IN %(item_groups)s"
		values["item_groups"] = tuple(item_groups)

	# -----------------------------
	# SUPPLIER GROUP TREE FILTER
	# -----------------------------

	if filters.get("supplier_group"):

		supplier_group = frappe.db.get_value(
			"Supplier Group",
			filters.get("supplier_group"),
			["lft", "rgt"],
			as_dict=1
		)

		supplier_groups = frappe.get_all(
			"Supplier Group",
			filters={
				"lft": [">=", supplier_group.lft],
				"rgt": ["<=", supplier_group.rgt]
			},
			pluck="name"
		)

		conditions += " AND sup.supplier_group IN %(supplier_groups)s"
		values["supplier_groups"] = tuple(supplier_groups)

	data = frappe.db.sql(
		  f"""

		SELECT

			poi.item_code,
			item.item_group,

			poi.item_name,
			poi.description,

			poi.qty,
			poi.uom,

			poi.rate,
			poi.amount,

			po.name AS purchase_order,

			po.transaction_date,

			po.supplier,
			po.supplier_name,

			sup.supplier_group,

			poi.project,

			poi.received_qty,

			po.per_billed,

			po.company,

			(
				poi.amount * IFNULL(po.per_billed, 0) / 100
			) AS billed_amt

		FROM `tabPurchase Order Item` poi

		INNER JOIN `tabPurchase Order` po
			ON po.name = poi.parent

		LEFT JOIN `tabItem` item
			ON item.name = poi.item_code

		LEFT JOIN `tabSupplier` sup
			ON sup.name = po.supplier

		WHERE
			po.docstatus = 1
			{conditions}

		ORDER BY
			po.transaction_date DESC

		""",
		values=values,
		as_dict=1
	)

	return data