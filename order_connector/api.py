import frappe
from erpnext.stock.dashboard.item_dashboard import get_data as get_item_balances

@frappe.whitelist()
def get_orders(name=None, limit=20):
    try:
        filters = {}
        orders = []
        if name:
            filters = {'name': name}
        order_parents = frappe.get_all('Order Request', fields=['name', 'partner_order_no', 'customer', 'customer_address', 'total_amount', 'status', 'docstatus', 'remarks', 'creation', 'modified', 'owner'], filters=filters, limit=limit, as_list=0)
        for order in order_parents:
            order_items = frappe.get_all('Order Request Item', fields=['item_name', 'description', 'unit', 'qty', 'price', 'amount'], filters={'parent': order.name}, limit=0)
            order.update({'items': order_items})
            orders.append(order)
        
        return orders
    except Exception as e:
        return e


@frappe.whitelist(allow_guest=True)
def insert_order(data):
    try:
        for item in data['items']:
            frappe.errprint(item)
            if item.get('item_name') == '' or item.get('item_name') == None:
                return "item_name cannot be empty"
        
        order_dict = {'doctype': 'Order Request'}
        order_dict.update(data)

        order = frappe.get_doc(order_dict)
        order = order.insert()
        return order.name
    
    except Exception as e:
        return e
        

@frappe.whitelist()
def get_items(item_code=None, limit=20):
    settings = get_packhouse_settings()

    lookup_warehouses = []
    
    if len(settings.lookup_warehouses) > 0:
        for w in settings.lookup_warehouses:
            lookup_warehouses.append(w.name)
    
    try:
        filters = {}
        item_list = []
        if item_code:
            filters = {'name': item_code}

        items = frappe.get_all('Item', fields=['item_code', 'item_name', 'description', 'stock_uom'], filters=filters, limit=limit)
        # items = frappe.get_all('Item', fields=['item_code', 'item_name', 'description', 'stock_uom'], filters=filters, limit=limit)
        for item in items:
            item_price = frappe.get_all('Item Price', fields=['price_list_rate'], filters={'item_code': item.item_code, 'selling': 1}, limit=1, order_by='creation desc')
            if len(item_price) > 0:
                item.update({'price': item_price[0].price_list_rate or 0})
            balances = get_item_balances(item.item_code)
            
            total_bal = 0
            if len(balances) > 0:
                for wb in balances:
                    if wb.warehouse in lookup_warehouses:
                        total_bal = total_bal + wb.actual_qty
                    else:
                        # use default WH
                        #frappe.get_value("Item", "Stock Settings", 'default_w')
                        total_bal = 0

            item.update({'balance': total_bal})
            
            item_list.append(item)
        
        return item_list
    
    except Exception as e:
        frappe.throw(e)

def get_packhouse_settings():
    return frappe.get_cached_doc('Packhouse Settings', 'Packhouse Settings')