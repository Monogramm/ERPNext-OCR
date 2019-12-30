# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"module_name": "OCR Read",
			"_doctype": "OCR Read",
			"color": "#00bcd4",
			"icon": "fa fa-eye",
			"type": "link",
			"link": "List/OCR Read"
		},

		{
			"module_name": "ERPNext OCR",
			"color": "#00bcd4",
			"icon": "octicon octicon-eye",
			"type": "module",
			"label": _("ERPNext OCR"),
			"hidden": 1
		}
	]
