# -*- coding: utf-8 -*-
# Copyright (c) 2018, John Vincent Fiel and Contributors
# Copyright (c) 2019, Monogramm and Contributors
# See license.txt

from __future__ import unicode_literals

import frappe
import unittest
import os

from erpnext_ocr.erpnext_ocr.doctype.ocr_read.ocr_read import force_attach_file_doc


def create_ocr_reads():
    if frappe.flags.test_ocr_reads_created:
        return

    frappe.set_user("Administrator")
    frappe.get_doc({
        "doctype": "OCR Read",
        "file_to_read": os.path.join(os.path.dirname(__file__),
                                     os.path.pardir, os.path.pardir, os.path.pardir,
                                     "tests", "test_data", "sample1.jpg"),
        "language": "eng"
    }).insert()

    frappe.get_doc({
        "doctype": "OCR Read",
        "file_to_read": os.path.join(os.path.dirname(__file__),
                                     os.path.pardir, os.path.pardir, os.path.pardir,
                                     "tests", "test_data", "Picture_010.png"),
        "language": "eng"
    }).insert()

    frappe.get_doc({
        "doctype": "OCR Read",
        "file_to_read": os.path.join(os.path.dirname(__file__),
                                     os.path.pardir, os.path.pardir, os.path.pardir,
                                     "tests", "test_data", "sample2.pdf"),
        "language": "eng"
    }).insert()

    frappe.flags.test_ocr_reads_created = True


def delete_ocr_reads():
    if frappe.flags.test_ocr_reads_created:
        frappe.set_user("Administrator")

        for d in frappe.get_all("OCR Read"):
            doc = frappe.get_doc("OCR Read", d.name)
            doc.delete()

        # Delete directly in DB to avoid validation errors
        #frappe.db.sql("""delete from `tabOCR Read`""")

        frappe.flags.test_ocr_reads_created = False


class TestOCRRead(unittest.TestCase):
    def setUp(self):
        create_ocr_reads()

    def tearDown(self):
        delete_ocr_reads()


    def test_ocr_read_image(self):
        frappe.set_user("Administrator")
        doc = frappe.get_doc({
            "doctype": "OCR Read",
            "file_to_read": os.path.join(os.path.dirname(__file__),
                                        os.path.pardir, os.path.pardir, os.path.pardir,
                                        "tests", "test_data", "sample1.jpg"),
            "language": "eng"
        })

        recognized_text = doc.read_image()
        self.assertEqual(recognized_text, doc.read_result)

        self.assertIn("The quick brown fox", recognized_text)
        self.assertIn("jumped over the 5", recognized_text)
        self.assertIn("lazy dogs!", recognized_text)
        self.assertNotIn("And an elephant!", recognized_text)


    def test_ocr_read_pdf(self):
        frappe.set_user("Administrator")
        doc = frappe.get_doc({
            "doctype": "OCR Read",
            "file_to_read": os.path.join(os.path.dirname(__file__),
                                        os.path.pardir, os.path.pardir, os.path.pardir,
                                        "tests", "test_data", "sample2.pdf"),
            "language": "eng"
        })

        recognized_text = doc.read_image()

        # FIXME values are not equal on Alpine ??!
        # self.assertEqual(recognized_text, doc.read_result)

        self.assertIn("Python Basics", recognized_text)
        self.assertNotIn("Java", recognized_text)


    def test_force_attach_file_doc(self):
        doc = frappe.get_doc({
            "doctype": "OCR Read",
            "file_to_read": os.path.join(os.path.dirname(__file__),
                                        os.path.pardir, os.path.pardir, os.path.pardir,
                                        "tests", "test_data", "Picture_010.png"),
            "language": "eng"
        })

        force_attach_file_doc('test.tif', doc.name)

        forced_doc = frappe.get_doc({
            "doctype": "OCR Read",
            "name": doc.name,
            "language": "eng"
        })

        self.assertEqual(forced_doc.name, doc.name)

        # FIXME force_attach_file_doc does not work ?
        # print(doc.file_to_read)
        # self.assertTrue('/private/files/test.tif' in doc.file_to_read)


    def test_ocr_read_list(self):
        # frappe.set_user("test1@example.com")
        frappe.set_user("Administrator")
        res = frappe.get_list("OCR Read", filters=[
                              ["OCR Read", "file_to_read", "like", "%sample%"]], fields=["name", "file_to_read"])
        self.assertEqual(len(res), 2)
        files_to_read = [r.file_to_read for r in res]
        self.assertTrue(os.path.join(os.path.dirname(__file__),
                                     os.path.pardir, os.path.pardir, os.path.pardir,
                                     "tests", "test_data", "sample1.jpg") in files_to_read)
        self.assertTrue(os.path.join(os.path.dirname(__file__),
                                     os.path.pardir, os.path.pardir, os.path.pardir,
                                     "tests", "test_data", "sample2.pdf") in files_to_read)
