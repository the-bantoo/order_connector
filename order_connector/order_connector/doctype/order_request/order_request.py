# Copyright (c) 2023, Bantoo and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import json
from frappe.model.document import Document
from erpnext.stock.dashboard.item_dashboard import get_data
from frappe.utils import today

class OrderRequest(Document):
	def onload(self):
		#self.setup_partner()
		pass
		
	@frappe.whitelist()
	def validate(self):
		self.validate_items(self.items)

	@frappe.whitelist()
	def calculate_totals(self):
		""" update items.balance, items.amount, doc.total_qty, doc.total_amount
		"""
		self.update_fields()

	@frappe.whitelist()
	def setup_partner(self):
		"""move this to ph settings
		"""
		user = frappe.get_doc("User", frappe.session.user)
		try:
			if user.partner:
				self.partner = user.partner
		except Exception as e:
			if e.__class__.__name__ == "AttributeError":
				self.create_custom_fields()
				self.setup_partner()
			else:
				frappe.throw(str(e))


	@frappe.whitelist()
	def lookup_address(self):
		partners = self.get_partners()

		if self.partner in partners:

			address = frappe.db.get_list("Address", filters= {"name": self.lookup_addr}, 
						fields = ['address_line1', 'address_line2', 'city', 'country', 'email_id', 'phone']
					)
			if len(address) > 0:
				address = address[0]
				self.customer = address.address_line1
				if address.email_id:
					self.email = address.email_id
				else:
					self.email = ''
				if address.phone:
					self.phone_number = address.phone
				else:
					self.phone_number = ''
				line2 = ''
				if address.address_line2:
					line2 = address.address_line2 + ', '
				self.customer_address = "{0}{1}, {2}".format(line2, address.city, address.country)
			

		else:
			customer = frappe.db.get_list("Customer", filters= {"name": self.lookup_customer},
					fields = ['customer_name', 'email_id', 'mobile_no']
				)
			if len(customer) > 0:
				customer = customer[0]
				self.customer = customer.customer_name
				self.email = customer.email_id
				self.phone_number = customer.mobile_no
				# add addr

	def on_submit(self):
		self.create_sales_order()
		
	def create_customer(self):
		last_customer = frappe.get_last_doc("Customer")
		if self.customer.startswith("New Customer"):
			frappe.throw(_('Customer Name cannot start with {0}').format(frappe.bold('"New Customer"')))
		
		customer_dict = {
			'doctype': 'Customer',
			'naming_series': last_customer.naming_series or 'CUST-.YYYY.-',
			'customer_name': self.customer.strip(),
			'customer_type': 'Company', # update
			'customer_group': "Commercial", # update
			'territory': "Lusaka"
		}
		if last_customer:
			customer_dict.update({
				'customer_type': last_customer.customer_type, 
				'customer_group': last_customer.customer_group,
				'territory': last_customer.territory,
			})
		frappe.errprint(customer_dict)
			
		customer = frappe.get_doc(customer_dict)
		customer = customer.insert()
		self.create_contact(self.customer, self.email, self.phone_number, customer.name)


	def create_contact(self, fullname, email, phone_number, customer_doc_name):
		contact = frappe.new_doc("Contact")
		contact.update({"first_name": fullname})
		if email:
			contact.update({"email_id": email})
			contact.append("email_ids", dict(email_id=email, is_primary=True))
		if phone_number:
			contact.append("phone_nos", dict(phone=phone_number, is_primary=True))

		contact.append("links", dict(link_doctype="Customer", link_name=customer_doc_name))
		contact.flags.ignore_mandatory = True
		contact.insert(ignore_permissions=True)

	def update_address(self):
		addr = frappe.get_doc("Address", self.customer)
		addr.address_line1 = self.customer
		
		if self.customer_address:
			trimmed_addr = self.customer_address.replace(self.customer, '', 1).replace(', Lusaka', '', 1).replace(', Zambia', '', 1).replace('Lusaka', '', 1).replace('Zambia', '', 1)
			if trimmed_addr != '':
				addr.address_line2 = trimmed_addr
		if self.email:
			addr.email_id = self.email
		if self.phone_number:
			addr.phone = self.phone_number
		addr.save(ignore_permissions=True)
		return addr.name

	def create_address(self):
		addr = frappe.new_doc("Address")
		addr.update({"name": self.customer})
		addr.update({"address_title": self.customer})
		addr.update({"country": "Zambia"})
		addr.update({"city": "Lusaka"})
		addr.update({"address_type": "Shipping"})
		addr.update({"address_line1": self.customer})
		if self.customer_address:
			addr.update({"address_line2": self.customer_address.replace(self.customer, '', 1).replace(', Lusaka', '', 1).replace(', Zambia', '', 1).replace('Lusaka', '', 1).replace('Zambia', '', 1)})
		addr.append("links", dict(link_doctype="Customer", link_name=self.partner))
		if self.email:
			addr.update({"email_id": self.email})
		if self.phone_number:
			addr.update({"phone", self.phone_number})
		addr.insert(ignore_permissions=True)
		return addr.name

	def get_partners(self):
		ph_settings = get_packhouse_settings()
		partners = []
		for p in ph_settings.active_partners:
			partners.append(p.partner)

		return partners

	def create_sales_order(self):
		""" create sales order_request and link it to Order Request
		check if item is matched
		"""
		partners = self.get_partners()

		customer = ''
		addr = None

		if self.partner and self.partner in partners:
			customer = self.partner
			if not frappe.db.exists("Address", self.customer.strip()):
				addr = self.create_address()
			else:
				addr = self.update_address()
		else:
			customer = self.customer
			if not frappe.db.exists("Customer", self.customer.strip()):
				# create the customer if this is not a partner sale
				self.create_customer()
			

		so_items = []
		for item in self.items:
			so_items.append({
				'item_code': item.item,
				'sku': item.sku,
				'processing_type': item.processing_type,
				'description': item.description,
				'rate': item.price,
				'uom': item.unit,
				'qty': item.qty,
				'warehouse': item.warehouse,
				'delivery_date': self.delivery_date
			})

		company = get_company()
		taxes = frappe.get_list('Sales Taxes and Charges Template', fields=['name'], filters={'is_default': 1}, order_by='creation asc', limit=1)
		so_dict = {
			'doctype': 'Sales Order',
			'customer': customer,
			'po_no': self.partner_order_no,
			'customer_address': addr,
			'shipping_address_name': addr,
			'transaction_date': self.order_date,
			'company': company.name,
			'currency': company.default_currency,
			'price_list': company.default_price_list,
			'delivery_date': self.delivery_date,
			'items': so_items
		}

		if addr:
			so_dict.update({'customer_address': addr, 'shipping_address_name': addr})
		if self.partner:
			so_dict.update({'sales_partner': self.partner})
		if self.partner:
			so_dict.update({'terms': self.remarks,})

		if len(taxes) != 0:
			so_dict.update({'taxes_and_charges': taxes[0].name})
			
		so_doc = frappe.get_doc(so_dict)
		so_doc.insert(ignore_mandatory=True)

		self.sales_order = so_doc.name
		self.status = "Accepted"
		self.save()
		
		#frappe.db.set_value("Order Request", self.name, {"sales_order": self.sales_order, "status": "Accepted"})




	def update_fields(self):
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
			item_name = item.sku
			if item.item:
				item_name = "{1} ({0})".format(item.sku, item.item)

			if item.qty < 1:
				frappe.throw(_("Row # {1}: {0} quantity cannot be less than 1").format(
					frappe.bold(item_name), frappe.bold(item.idx)
				))
			#product = frappe.get_doc("Product", item.)
			if not item.price or item.price == 0:
				item.price = frappe.get_doc('Product', item.sku).price
			if item.price < 1:
				frappe.throw(_("Row # {1}: {0} price cannot be less than 1").format(
					frappe.bold(item_name), frappe.bold(item.idx)
				))
		self.calculate_totals()

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
			# 	- When unit changes: convert to new unit if there's a conversion factor in item, otherwise it should be provided in the order_request item line (add fields similar to EF)
		
		# find a way to get the item balance using get_data, and assign it to self.bal
		for item in self.items:
			item_price = frappe.get_all('Item Price', fields=['price_list_rate'], filters={'item_code': item.item, 'selling': 1}, limit=1, order_by='creation desc')
			item_uom = frappe.get_value('Item', item.item, 'stock_uom')
			
			item.unit = item_uom
			if item.item:
				bal = get_data(item.item)
				if len(bal)>0:
					item.balance = bal[0].actual_qty
					item.warehouse = bal[0].warehouse
				else:
					item.balance = 0
					item_doc = frappe.get_doc("Item", item.item)
					if item_doc.is_stock_item == 1:
						item.warehouse = item_doc.item_defaults[0].default_warehouse
					else:
						item.warehouse = ""
			else:
				item.balance = 0
				item.warehouse = ""

			if len(item_price) > 0:
				item.price = item_price[0].price_list_rate or 0
			
			

		packhouse_settings = get_packhouse_settings()
		# packhouse_settings.default_warehouse_first
		# packhouse_settings.lookup_warehouses
		# packhouse_settings.excluded_warehouses

	def create_custom_fields(self):
		update = False
		doctype = 'Customer'
		custom_fields = frappe.get_all("Custom Field", fields=["fieldname"], pluck="fieldname", limit=0)

		try:
			#if 'customer_address' in custom_fields:
			#	return

			doctype = 'Customer'	
					
			"""frappe.get_doc({
				"doctype": "Custom Field",
				"dt": doctype,
				"fieldname": "customer_address",
				"fieldtype": "Data",
				"label": "Sync Status",
				"insert_after": 'address_html',
				"allow_on_submit": 1,
				"no_copy": 1,
				"print_hide": 1,
				"hidden": 1
			}).insert()
			update = True
			"""
			if 'partner_section' not in custom_fields:
				partner_section = frappe.get_doc({
					"doctype": "Custom Field",
					"dt": "User",
					"fieldname": "partner_section",
					"fieldtype": "Section Break",
					"label": "Partner Information",
					"insert_after": 'enabled',
				})
				partner_section.ignore_permissions = True
				partner_section.insert()
				doctype = "User"
				update = True

			if 'partner' not in custom_fields:
				partner = frappe.get_doc({
					"doctype": "Custom Field",
					"dt": "User",
					"fieldname": "partner",
					"fieldtype": "Link",
					"options": "Customer",
					"label": "Partner",
					"insert_after": 'partner_section',
					"no_copy": 1,
					"print_hide": 1
				})
				partner.ignore_permissions = True
				partner.insert()
				doctype = "User"
				update = True

			if update:
				frappe.msgprint(_("A custom field has been added to {1}").format(frappe.bold('Customer Address'), doctype))
		except Exception as e:
			#create_custom_fields(doctype)
			count = 0
			while count < 1:
				# try again
				self.create_custom_fields()
				count += 1

			if count >= 1:
				frappe.msgprint(
					msg=_("Unable to create custom field(s). ") + e.message, 
					title=_('Database query failure'),
					raise_exception=1
				)
				count += 1
			
def get_packhouse_settings():
	return frappe.get_cached_doc("Packhouse Settings")

def get_company():
	return frappe.get_list('Company', fields=['*'], order_by='creation asc', limit=1)[0]