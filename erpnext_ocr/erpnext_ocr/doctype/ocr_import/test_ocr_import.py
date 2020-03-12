# -*- coding: utf-8 -*-
# Copyright (c) 2020, Monogramm and Contributors
# See license.txt
from __future__ import unicode_literals

import datetime
import os
import unittest

import frappe
from erpnext_ocr.erpnext_ocr.doctype.ocr_import.constants import TEST_RESULT_FOR_SI, TEST_RESULT_FOR_ITEM
from erpnext_ocr.erpnext_ocr.doctype.ocr_import.ocr_import import generate_doctype

# test recodes will automatically be generated by frappe
test_data = frappe.get_test_records('OCR Import')


class TestOCRImport(unittest.TestCase):
    def setUp(self):
        before_tests()
        frappe.set_user("Administrator")
        self.item_ocr_read = frappe.get_doc(
            {"doctype": "OCR Read", "file_to_read": os.path.join(os.path.dirname(__file__),
                                                                 os.path.pardir, os.path.pardir,
                                                                 os.path.pardir,
                                                                 "tests", "test_data",
                                                                 "item.pdf"), "language": "eng"})
        self.item_ocr_read.ocr_import = "Item"
        # self.item_ocr_read.read_image()
        self.item_ocr_read.read_result = TEST_RESULT_FOR_ITEM

        # Creating OCR Read doctype for Sales Invoice
        self.sales_invoice_ocr_read = frappe.get_doc(
            {"doctype": "OCR Read", "file_to_read": os.path.join(os.path.dirname(__file__),
                                                                 os.path.pardir, os.path.pardir,
                                                                 os.path.pardir,
                                                                 "tests", "test_data",
                                                                 "Picture_010.png"), "language": "eng"})
        # self.sales_invoice_ocr_read.read_image()
        self.sales_invoice_ocr_read.read_result = TEST_RESULT_FOR_SI
        if frappe.__version__[:2] != "10":
            comp = frappe.get_doc("Company", "_Test Company")
            comp.stock_adjustment_account = frappe.get_all("Account")[0]['name']
            comp.save()
            global_default = frappe.get_doc("Global Defaults")
            global_default.default_company = "_Test Company"
            global_default.current_fiscal_year = '_Test Fiscal Year 2012'
            global_default.save()

    def tearDown(self):
        self.item_ocr_read.delete()
        self.sales_invoice_ocr_read.delete()
        stock_entries = frappe.get_all("Stock Entry",
                                       filters=[['total_amount', '=', '15129'], ['docstatus', '!=', '2']])
        for entry in stock_entries:
            frappe.get_doc("Stock Entry", entry).cancel()

    def test_generate_doctype_item(self):
        item_ocr_import = frappe.get_doc("OCR Import", "Item")
        generated_item = generate_doctype(item_ocr_import.name, self.item_ocr_read.read_result, ignore_mandatory=True)
        self.assertEqual(generated_item.item_code, "fdsa")
        self.assertEqual(generated_item.item_group, "Consumable")
        generated_item.delete()

    def test_generating_sales_invoice(self):
        set_date_format("dd/mm/yyyy")
        sales_invoice_ocr_import = frappe.get_doc("OCR Import", "Sales Invoice")
        self.assertRaises(frappe.ValidationError, generate_doctype, sales_invoice_ocr_import.name,
                          self.sales_invoice_ocr_read.read_result)  # Due date before now
        # read_result = self.sales_invoice_ocr_read.read_result.encode('ascii', errors="ignore").replace("03/12/2006",
        #                                                                                                "03/12/2099")
        read_result = self.sales_invoice_ocr_read.read_result
        sales_invoice = generate_doctype(sales_invoice_ocr_import.name, read_result, ignore_mandatory=True,
                                         ignore_validate=True)

        self.assertEqual(sales_invoice.due_date, datetime.datetime(2006, 3, 12, 0, 0))
        self.assertEqual(sales_invoice.party_account_currency,
                         frappe.get_doc("Company", frappe.get_all("Company")[0]).default_currency)



def set_date_format(date_format):
    settings = frappe.get_doc("System Settings")
    settings.date_format = date_format
    settings.save()


def before_tests():
    frappe.clear_cache()
    # complete setup if missing
    from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
    if not frappe.get_list("Company"):
        setup_complete({
            "currency": "USD",
            "full_name": "Test User",
            "company_name": "Wind Power LLC",
            "timezone": "America/New_York",
            "company_abbr": "WP",
            "industry": "Manufacturing",
            "country": "United States",
            "fy_start_date": "2020-01-01",
            "fy_end_date": "2020-12-31",
            "language": "english",
            "company_tagline": "Testing",
            "email": "test@erpnext.com",
            "password": "test",
            "chart_of_accounts": "Standard",
            "domains": ["Manufacturing"],
        })

    frappe.db.sql("delete from `tabLeave Allocation`")
    frappe.db.sql("delete from `tabLeave Application`")
    frappe.db.sql("delete from `tabSalary Slip`")
    frappe.db.sql("delete from `tabItem Price`")

    frappe.db.set_value("Stock Settings", None, "auto_insert_price_list_rate_if_missing", 0)

    frappe.db.commit()
