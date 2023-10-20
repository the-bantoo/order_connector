# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from frappe.model.document import Document
from erpnext.stock.dashboard.item_dashboard import get_data

class Order(Document):
	@frappe.whitelist()
	def validate(self):
		""" update items.balance, items.amount, doc.total_qty, doc.total_amount
		"""
		self.update_fields()
		self.validate_items(self.items)

	def update_fields(self):
		#frappe.errprint(self.total_qty)

		self.total_qty = 0
		self.total_amount = 0
		for item in self.items:
			item.amount = item.qty * item.price
			self.total_qty = self.total_qty + item.qty
			self.total_amount = self.total_amount + item.amount

	def validate_items(self, items):
		""" ensure no negatives in qty or price
		"""
		for item in items:
			if item.qty < 1:
				frappe.throw(_("Row # {1}: {0} quantity cannot be less than 1").format(
					frappe.bold(item.item_name), frappe.bold(item.idx)
				))
			if item.price < 1:
				frappe.throw(_("Row # {1}: {0} price cannot be less than 1").format(
					frappe.bold(item.item_name), item.idx
				))			

	@frappe.whitelist()
	def update_item_balance(self):
			# Now (priority 1)
			# 	- Item Stock Balance and Warehouse
			# 	- Event: Update on Item Code selection		
			# 	- Lookup Logic
			# 		- Default Item WH (packhouse_settings.default_warehouse_first)
			# 		- Lookup WHs (packhouse_settings.lookup_warehouses)
			# 		- All Others, except Exclusion list (packhouse_settings.excluded_warehouses)
			# Next (priority 2):
			# 	- When unit changes: convert to new unit if there's a conversion factor in item, otherwise it should be provided in the order item line (add fields similar to EF)
		
		# find a way to get the item balance using get_data, and assign it to self.bal

		for item in self.items:
			if item.item:
				self.bal = get_data(item.item)
				if len(self.bal)>0:
					leng = len(self.bal)
					item.balance = self.bal[0].actual_qty
					item.warehouse = self.bal[0].warehouse
				else:
					item.balance = 0
					item.warehouse = " "
			else:
				item.balance = 0
				item.warehouse = " "
			

		packhouse_settings = get_packhouse_settings()
		# packhouse_settings.default_warehouse_first
		# packhouse_settings.lookup_warehouses
		# packhouse_settings.excluded_warehouses

def get_packhouse_settings():
	return frappe.get_cached_doc("Packhouse Settings")