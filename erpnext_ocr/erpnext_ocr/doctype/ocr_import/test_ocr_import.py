# -*- coding: utf-8 -*-
# Copyright (c) 2019, Monogramm and Contributors
# See license.txt
from __future__ import unicode_literals

import datetime
import os
import unittest

import frappe
from erpnext_ocr.erpnext_ocr.doctype.ocr_import.constants import TEST_RESULT_FOR_SI,TEST_RESULT_FOR_ITEM
from erpnext_ocr.erpnext_ocr.doctype.ocr_import.ocr_import import generate_doctype

# data will generated by frappe automatically
test_data = frappe.get_test_records('OCR Import')


class TestOCRImport(unittest.TestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        self.item_ocr_read = frappe.get_doc(
            {"doctype": "OCR Read", "file_to_read": os.path.join(os.path.dirname(__file__),
                                                                 os.path.pardir, os.path.pardir,
                                                                 os.path.pardir,
                                                                 "tests", "test_data",
                                                                 "item.pdf"), "language": "eng"})
        # Creating OCR Import doc
        if not frappe.db.exists("OCR Import", "Item"):
            self.item_ocr_import = frappe.new_doc("OCR Import")
            self.item_ocr_import.name = "Item"
            self.item_ocr_import.doctype_link = "Item"
            self.item_ocr_import.insert(ignore_permissions=True)
            self.item_ocr_import.save()
        self.item_ocr_read.ocr_import = self.item_ocr_import.name
        self.item_ocr_read.read_image()
        self.item_ocr_read.read_result = TEST_RESULT_FOR_ITEM

        # Creating OCR Read doctype
        self.sales_invoice_ocr_read = frappe.get_doc(
            {"doctype": "OCR Read", "file_to_read": os.path.join(os.path.dirname(__file__),
                                                                 os.path.pardir, os.path.pardir,
                                                                 os.path.pardir,
                                                                 "tests", "test_data",
                                                                 "Picture_010.png"), "language": "eng"})
        self.sales_invoice_ocr_read.read_image()
        self.sales_invoice_ocr_read.read_result = TEST_RESULT_FOR_SI

        self.list_with_items_for_si = create_items_for_sales_invoices()

    def tearDown(self):
        self.item_ocr_read.delete()
        self.item_ocr_import.delete()
        self.sales_invoice_ocr_read.delete()
        stock_entries = frappe.get_all("Stock Entry",
                                       filters=[['total_amount', '=', '15129'], ['docstatus', '!=', '2']])
        for entry in stock_entries:
            frappe.get_doc("Stock Entry", entry).cancel()

    def test_generating_item(self):
        item_code_mapping = frappe.get_doc(
            {"doctype": "OCR Import Mapping", "field": "item_code", "regexp": "Item Code (\\w+)",
             "parenttype": "OCR Import", "value_type": "Regex group", "parent": "Item"})
        item_code_mapping.save(ignore_permissions=True)
        item_group_mapping = frappe.get_doc(
            {"doctype": "OCR Import Mapping", "value_type": "Regex group", "field": "item_group",
             "regexp": "Item Group (\\w+)",
             "parenttype": "OCR Import", "parent": "Item"})
        item_group_mapping.save(ignore_permissions=True)
        self.item_ocr_import.append("mappings", item_code_mapping.__dict__)
        self.item_ocr_import.append("mappings", item_group_mapping.__dict__)
        self.item_ocr_import.save()
        generated_item = generate_doctype(self.item_ocr_import.name, self.item_ocr_read.read_result)
        self.assertEqual(generated_item.item_code, "fdsa")
        self.assertEqual(generated_item.item_group, "Consumable")
        generated_item.delete()

    def test_generating_sales_invoice(self):
        set_date_format("dd/mm/yyyy")
        sales_invoice_ocr_import = frappe.get_doc("OCR Import", "Sales Invoice")
        self.assertRaises(frappe.ValidationError, generate_doctype, sales_invoice_ocr_import.name,
                          self.sales_invoice_ocr_read.read_result)  # Due date before now
        read_result = self.sales_invoice_ocr_read.read_result.replace("03/12/2006", "03/12/2026")
        sales_invoice = generate_doctype(sales_invoice_ocr_import.name, read_result)

        self.assertEqual(sales_invoice.due_date, datetime.datetime(2026, 12, 3, 0, 0))
        self.assertEqual(sales_invoice.party_account_currency,
                         frappe.get_doc("Company", frappe.get_all("Company")[0]).default_currency)


def create_items_for_sales_invoices():
    """
    Create some items for Picture_010.png Sales Invoice
    :return:
    """
    list_with_items_for_si = []
    if not frappe.db.exists("Item", "JO.2"):
        jo_2 = frappe.get_doc(
            {"doctype": "Item", "item_name": "JO.2", "item_code": "JO.2", "item_group": "Consumable",
             "stock_uom": "Nos",
             "opening_stock": "123", "standard_rate": "123"})
        jo_2.save()
        list_with_items_for_si.append(jo_2)
    if not frappe.db.exists("Item", "Vi.2"):
        vi_2 = frappe.get_doc(
            {"doctype": "Item", "item_name": "Vi.2", "item_code": "Vi.2", "item_group": "Consumable",
             "stock_uom": "Nos",
             "opening_stock": "123", "standard_rate": "123"})
        vi_2.save()
        list_with_items_for_si.append(vi_2)
    if not frappe.db.exists("Item", "JO.1"):
        jo_1 = frappe.get_doc(
            {"doctype": "Item", "item_name": "JO.1", "item_code": "JO.1", "item_group": "Consumable",
             "stock_uom": "Nos",
             "opening_stock": "123", "standard_rate": "123"})
        jo_1.save()
        list_with_items_for_si.append(jo_1)
    if not frappe.db.exists("Item", "SERVICE D COMPLETE OVERHAUL"):
        service_d_overhaul = frappe.get_doc(
            {"doctype": "Item", "item_name": "SERVICE D COMPLETE OVERHAUL", "item_code": "SERVICE D COMPLETE OVERHAUL",
             "item_group": "Consumable", "stock_uom": "Nos",
             "opening_stock": "123", "standard_rate": "123"})
        service_d_overhaul.save()
        list_with_items_for_si.append(service_d_overhaul)
    if not frappe.db.exists("Item", "SERVICE D"):
        service_d = frappe.get_doc(
            {"doctype": "Item", "item_name": "SERVICE D", "item_code": "SERVICE D",
             "item_group": "Consumable", "stock_uom": "Nos",
             "opening_stock": "123", "standard_rate": "123"})
        service_d.save()
        list_with_items_for_si.append(service_d)
    if not frappe.db.exists("Item", "AL465.0"):
        al_465 = frappe.get_doc(
            {"doctype": "Item", "item_name": "AL465.0", "item_code": "AL465.0",
             "item_group": "Consumable", "stock_uom": "Nos",
             "opening_stock": "123", "standard_rate": "123"})
        al_465.save()
        list_with_items_for_si.append(al_465)
    return list_with_items_for_si


def set_date_format(date_format):
    settings = frappe.get_doc("System Settings")
    settings.date_format = date_format
    settings.save()
