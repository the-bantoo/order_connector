# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class Product(Document):
	def validate(self):
		self.update_fields()

	def update_fields(self):
		if not self.item_code:
			self.approved = 0
			# if self.disabled == 0:
			# 	self.disabled = 1

		else:
			self.approved = 1
			if self.disabled == 0:
				frappe.msgprint(_("{0} is now available in Sales Transactions as {1}. <br>You can change anytime this by ticking <strong>Disabled</strong>").format(self.product_name, frappe.bold(self.item_code)))


	# def after_insert(self):
	# 	pass