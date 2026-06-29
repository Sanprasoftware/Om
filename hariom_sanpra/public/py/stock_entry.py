import frappe
import json
from frappe.utils import flt, cint


def _get_stock_uom(item_code):
    if not item_code:
        return None
    return frappe.db.get_value("Item", item_code, "stock_uom")


def _get_raw_rows(doc):
    grouped_rows = {}

    for row in doc.get("custom_raw_items") or []:
        warehouse = row.get("warehouse")
        item_code = row.get("item")
        qty = flt(row.get("qty"))

        if not (warehouse or item_code or qty):
            continue

        if not warehouse:
            frappe.throw("Please fill Warehouse in all Custom Raw Items rows")

        if not item_code:
            frappe.throw("Please fill Item in all Custom Raw Items rows")

        if qty <= 0:
            frappe.throw("Qty must be greater than 0 in all Custom Raw Items rows")

        key = (
            warehouse,
            item_code,
            row.get("batch"),
            flt(row.get("size_1")),
            flt(row.get("size_2")),
        )

        if key not in grouped_rows:
            grouped_rows[key] = {
                "warehouse": warehouse,
                "item_code": item_code,
                "qty": 0,
                "batch": row.get("batch"),
                "size_1": flt(row.get("size_1")),
                "size_2": flt(row.get("size_2")),
            }

        grouped_rows[key]["qty"] += qty

    return list(grouped_rows.values())


@frappe.whitelist()
def add_items(doc):
    if isinstance(doc, str):
        doc = json.loads(doc)

    doc = frappe.get_doc(doc)

    if doc.purpose != "Repack":
        return doc

    raw_rows = _get_raw_rows(doc)

    fg_warehouse = doc.custom_warehouse
    fg_item = doc.custom_item_code
    fg_count = cint(doc.custom_qty)
    fg_batch = doc.custom_batch
    size1 = flt(doc.custom_size_1)
    size2 = flt(doc.custom_size_2)

    wastage_warehouse = doc.custom_wastage_warehouse
    wastage_item = doc.custom_wastage_item
    wastage_qty = flt(doc.custom_wastage_qty)
    wastage_batch = doc.custom_wastage_batch

    if not raw_rows:
        frappe.throw("Please add at least one row in Custom Raw Items with Warehouse, Item and Qty")

    if not (fg_warehouse and fg_item and fg_count):
        frappe.throw("Please fill Custom Warehouse, Custom Item Code and Custom Qty")

    if fg_count <= 0:
        frappe.throw("Custom Qty must be greater than 0")

    if wastage_qty < 0:
        frappe.throw("Custom Wastage Qty cannot be negative")

    total_raw_qty = sum(flt(row.get("qty")) for row in raw_rows)
    net_qty = flt(total_raw_qty) - flt(wastage_qty)

    if net_qty <= 0:
        frappe.throw("Net qty (Raw Qty - Wastage Qty) must be greater than 0")

    per_row_qty = flt(net_qty) / flt(fg_count)

    fg_uom = _get_stock_uom(fg_item)
    wastage_uom = _get_stock_uom(wastage_item)

    doc.set("items", [])

    # 🔹 RAW ITEMS
    for raw_row in raw_rows:
        doc.append("items", {
            "item_code": raw_row["item_code"],
            "qty": flt(raw_row["qty"]),
            "s_warehouse": raw_row["warehouse"],
            "batch_no": raw_row["batch"],
            "uom": _get_stock_uom(raw_row["item_code"]),
            "is_finished_item": 0,
            "is_scrap_item": 0,
            "custom_size_1": flt(raw_row["size_1"]),
            "custom_size_2": flt(raw_row["size_2"]),
        })

    # 🔹 FG ITEMS (split rows)
    for _ in range(fg_count):
        doc.append("items", {
            "item_code": fg_item,
            "qty": per_row_qty,
            "t_warehouse": fg_warehouse,
            "batch_no": fg_batch,
            "uom": fg_uom,
            "is_finished_item": 1,
            "is_scrap_item": 0,
            "custom_size_1": size1,
            "custom_size_2": size2,
            "set_basic_rate_manually": 1,
        })

    # 🔹 WASTAGE
    if wastage_qty > 0:
        if not (wastage_warehouse and wastage_item):
            frappe.throw("Please fill Custom Wastage Warehouse and Custom Wastage Item when Custom Wastage Qty is set")

        doc.append("items", {
            "item_code": wastage_item,
            "qty": wastage_qty,
            "t_warehouse": wastage_warehouse,
            "batch_no": wastage_batch,
            "uom": wastage_uom,
            "is_finished_item": 0,
            "is_scrap_item": 1,
            "set_basic_rate_manually": 1,
        })

    return doc
@frappe.whitelist()
def calculation(doc, Method=None):
    for row in doc.items:
        if doc.stock_entry_type == "GD REWINDING":
            hanging_weight = flt(row.custom_hanging_weight)
            core_weight = flt(row.custom_core_weight)
            roll_size_inches = flt(row.custom_roll_actual_size_inches)
            roll_meter = flt(row.custom_roll_meter)

            row.custom_net_weight = hanging_weight - core_weight
            row.custom_roll_sqr_meter = (roll_size_inches / 39.37) * roll_meter

            if flt(row.custom_roll_sqr_meter) > 0:
                row.custom_roll_actual_gsm = (flt(row.custom_net_weight) / flt(row.custom_roll_sqr_meter)) * 1000
            else:
                row.custom_roll_actual_gsm = 0
        
        if doc.stock_entry_type == "JOINT M/C":

            # 👉 GSM from custom_raw_items table
            gsm = 0
            if doc.custom_raw_items:
                for d in doc.custom_raw_items:
                    if flt(d.gsm):
                        gsm = flt(d.gsm)
                        break   # first valid gsm

            # 👉 formula same (only gsm source changed)
            row.custom_output_weight = (
                flt(row.custom_size_1) *
                flt(row.custom_size_2) *
                ((gsm / 1000) / 10.758)
            )

            # 👉 qty update only for FG
            if row.is_finished_item == 1:
                row.qty = row.custom_output_weight


@frappe.whitelist()
def set_batch(doc, Method=None):
    if doc.items:
        for row in doc.items:
            batch = frappe.get_value("Item", row.item_code, "custom_batch")
            if batch:
                # frappe.set_value("Stock Entry Detail", row.name, "batch_no", batch)
                row.batch_no = batch

def _get_small_item_rows(doc):
    rows = []

    for row in doc.get("custom_rk__small_items") or []:
        warehouse = row.get("warehouse")
        item_code = row.get("item")
        qty = flt(row.get("qty"))
        qty_count = cint(qty)

        if not (warehouse or item_code or qty):
            continue

        if not warehouse:
            frappe.throw("Please fill Warehouse in all RK - Small Items rows")

        if not item_code:
            frappe.throw("Please fill Item in all RK - Small Items rows")

        if qty <= 0:
            frappe.throw("Qty must be greater than 0 in all RK - Small Items rows")

        if qty != qty_count:
            frappe.throw("Qty in RK - Small Items must be a whole number")

        rows.append(
            {
                "warehouse": warehouse,
                "item_code": item_code,
                "qty": qty_count,
                "batch": row.get("batch"),
                "meter_length": flt(row.get("meter_length")),
                "line_meter": row.get("line_meter"),
                "trimkg": flt(row.get("trimkg")),
            }
        )

    return rows


@frappe.whitelist()
def add_items(doc):
    if isinstance(doc, str):
        doc = json.loads(doc)

    doc = frappe.get_doc(doc)

    if doc.purpose != "Repack":
        return doc

    raw_rows = _get_raw_rows(doc)

    fg_warehouse = doc.custom_warehouse
    fg_item = doc.custom_item_code
    fg_count = cint(doc.custom_qty)
    fg_batch = doc.custom_batch
    size1 = flt(doc.custom_size_1)
    size2 = flt(doc.custom_size_2)

    wastage_warehouse = doc.custom_wastage_warehouse
    wastage_item = doc.custom_wastage_item
    wastage_qty = flt(doc.custom_wastage_qty)
    wastage_batch = doc.custom_wastage_batch

    if not raw_rows:
        frappe.throw("Please add at least one row in Custom Raw Items with Warehouse, Item and Qty")

    if not (fg_warehouse and fg_item and fg_count):
        frappe.throw("Please fill Custom Warehouse, Custom Item Code and Custom Qty")

    if fg_count <= 0:
        frappe.throw("Custom Qty must be greater than 0")

    if wastage_qty < 0:
        frappe.throw("Custom Wastage Qty cannot be negative")

    total_raw_qty = sum(flt(row.get("qty")) for row in raw_rows)
    net_qty = flt(total_raw_qty) - flt(wastage_qty)

    if net_qty <= 0:
        frappe.throw("Net qty (Raw Qty - Wastage Qty) must be greater than 0")

    per_row_qty = flt(net_qty) / flt(fg_count)
    fg_uom = _get_stock_uom(fg_item)
    wastage_uom = _get_stock_uom(wastage_item)

    doc.set("items", [])

    for raw_row in raw_rows:
        doc.append(
            "items",
            {
                "item_code": raw_row["item_code"],
                "qty": flt(raw_row["qty"]),
                "s_warehouse": raw_row["warehouse"],
                "batch_no": raw_row["batch"],
                "uom": _get_stock_uom(raw_row["item_code"]),
                "is_finished_item": 0,
                "is_scrap_item": 0,
                "custom_size_1": flt(raw_row["size_1"]),
                "custom_size_2": flt(raw_row["size_2"]),
            },
        )

    for _ in range(fg_count):
        doc.append(
            "items",
            {
                "item_code": fg_item,
                "qty": per_row_qty,
                "t_warehouse": fg_warehouse,
                "batch_no": fg_batch,
                "uom": fg_uom,
                "is_finished_item": 1,
                "is_scrap_item": 0,
                "custom_size_1": size1,
                "custom_size_2": size2,
                "set_basic_rate_manually": 1,
            },
        )

    if wastage_qty > 0:
        if not (wastage_warehouse and wastage_item):
            frappe.throw(
                "Please fill Custom Wastage Warehouse and Custom Wastage Item when Custom Wastage Qty is set"
            )

        doc.append(
            "items",
            {
                "item_code": wastage_item,
                "qty": wastage_qty,
                "t_warehouse": wastage_warehouse,
                "batch_no": wastage_batch,
                "uom": wastage_uom,
                "is_finished_item": 0,
                "is_scrap_item": 1,
                "set_basic_rate_manually": 1,
            },
        )

    return doc


@frappe.whitelist()
def add_rk_items(doc):
    if isinstance(doc, str):
        doc = json.loads(doc)

    doc = frappe.get_doc(doc)

    if doc.purpose != "Repack":
        return doc

    raw_rows = _get_raw_rows(doc)
    small_item_rows = _get_small_item_rows(doc)

    wastage_warehouse = doc.custom_wastage_warehouse
    wastage_item = doc.custom_wastage_item
    wastage_qty = flt(doc.custom_wastage_qty)
    wastage_batch = doc.custom_wastage_batch

    if not raw_rows:
        frappe.throw("Please add at least one row in Custom Raw Items with Warehouse, Item and Qty")

    if not small_item_rows:
        frappe.throw("Please add at least one row in RK - Small Items with Warehouse, Item and Qty")

    if wastage_qty < 0:
        frappe.throw("Custom Wastage Qty cannot be negative")

    doc.set("items", [])

    for raw_row in raw_rows:
        doc.append(
            "items",
            {
                "item_code": raw_row["item_code"],
                "qty": flt(raw_row["qty"]),
                "s_warehouse": raw_row["warehouse"],
                "batch_no": raw_row["batch"],
                "uom": _get_stock_uom(raw_row["item_code"]),
                "is_finished_item": 0,
                "is_scrap_item": 0,
                "custom_size_1": flt(raw_row["size_1"]),
                "custom_size_2": flt(raw_row["size_2"]),
            },
        )

    for row in small_item_rows:
        fg_uom = _get_stock_uom(row["item_code"])

        for _ in range(row["qty"]):
            doc.append(
                "items",
                {
                    "item_code": row["item_code"],
                    "qty": 1,
                    "t_warehouse": row["warehouse"],
                    "batch_no": row["batch"],
                    "uom": fg_uom,
                    "is_finished_item": 1,
                    "is_scrap_item": 0,
                    "custom_meter_length": row["meter_length"],
                    "custom_line_meter": row["line_meter"],
                    "custom_trimkg": row["trimkg"],
                    "set_basic_rate_manually": 1,
                },
            )

    if wastage_qty > 0:
        if not (wastage_warehouse and wastage_item):
            frappe.throw(
                "Please fill Custom Wastage Warehouse and Custom Wastage Item when Custom Wastage Qty is set"
            )

        doc.append(
            "items",
            {
                "item_code": wastage_item,
                "qty": wastage_qty,
                "t_warehouse": wastage_warehouse,
                "batch_no": wastage_batch,
                "uom": _get_stock_uom(wastage_item),
                "is_finished_item": 0,
                "is_scrap_item": 1,
                "set_basic_rate_manually": 1,
            },
        )

    return doc
# @frappe.whitelist()
# def calculate_total_wastage(doc, method=None):
#     doc.custom_total_wastage = (
#         flt(doc.custom_ld) +
#         flt(doc.custom_trim) +
#         flt(doc.custom_other)
#     )


@frappe.whitelist()
def get_finished_qty(doc, method=None):
    total = 0.0  
    if doc.items:
        for row in doc.items:
            if cint(row.is_finished_item) == 1:
                total += flt(row.qty)
            if doc.purpose == "Manufacture" and row.is_finished_item == 1:
                doc.custom_job_name = row.item_code
    doc.custom_total_qty = total

#*******************************************************************************************************
def set_job_name(doc, method=None):
    finished_items = []

    for row in doc.items:
        if row.is_finished_item:
            finished_items.append(row.item_code)

    if finished_items:
        doc.custom_job_name = ", ".join(finished_items)

