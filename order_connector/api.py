import frappe
from frappe import _
from erpnext.stock.dashboard.item_dashboard import get_data as get_item_balances

@frappe.whitelist()
def get_orders(name=None, limit=20):
    try:
        filters = {}
        orders = []
        if name:
            filters = {'name': name}
        order_parents = frappe.get_all('Order Request', fields=['name', 'partner_order_no', 'customer', 'customer_address', 'phone_number', 'gps_coordinates', 'total_amount', 'status', 'remarks', 'creation', 'modified', 'owner'], filters=filters, limit=limit, as_list=0)
        for order in order_parents:
            order_items = frappe.get_all('Order Request Item', fields=['sku', 'processing_type', 'description', 'unit', 'qty', 'price', 'amount', 'status'], filters={'parent': order.name}, limit=0)
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
            if item.get('sku') == '' or item.get('sku') == None:
                return "sku cannot be empty"
        
        order_dict = {'doctype': 'Order Request'}
        order_dict.update(data)

        order = frappe.get_doc(order_dict)
        order = order.insert()
        return order.name
    
    except Exception as e:
        return e
        

@frappe.whitelist()
def get_items_OLD(item_code=None, limit=20):
    settings = get_packhouse_settings()

    lookup_warehouses = []
    
    for w in settings.lookup_warehouses:
        lookup_warehouses.append(w.name)
    
    try:
        filters = {}
        item_list = []
        if item_code:
            filters = {'name': item_code}
        from order_connector.order_connector.doctype.order_request.order_request import get_company
        items = frappe.get_all('Item', fields=['item_code', 'item_name', 'description', 'stock_uom'], filters=filters, limit=limit)
        item_defaults = frappe.get_all('Item Default', fields=['default_warehouse'], filters={'company': get_company().name}, limit=10)
        for item in items:
            item_price = frappe.get_all('Item Price', fields=['price_list_rate'], filters={'item_code': item.item_code, 'selling': 1}, limit=1, order_by='creation desc')
            if len(item_price) > 0:
                item.update({'price': item_price[0].price_list_rate or 0})
            balances = get_item_balances(item.item_code)
            
            total_bal = 0
            for wb in balances:
                if (wb.warehouse in lookup_warehouses) or (wb.warehouse == item_defaults[0].default_warehouse):
                    total_bal = total_bal + wb.actual_qty

            item.update({'balance': total_bal})
            
            item_list.append(item)
        
        return item_list
    
    except Exception as e:
        frappe.throw(e)


@frappe.whitelist()
def get_products(sku=None, limit=20):
    settings = get_packhouse_settings()

    lookup_warehouses = []
    
    for w in settings.lookup_warehouses:
        lookup_warehouses.append(w.name)

    """
        get products
        for products with item do the rest, else, NONE
    """
    
    try:
        filters = {}
        item_list = []
        if sku:
            filters = {'sku': sku}
        from order_connector.order_connector.doctype.order_request.order_request import get_company
        products = frappe.get_all('Product', fields=['sku', 'product_name', 'description', 'product_category', 'processing_type', 'item_code', 'approved', 'disabled'], filters=filters, limit=limit)
        #items = frappe.get_all('Item', fields=['item_code', 'item_name', 'description', 'stock_uom'], filters=filters, limit=limit)
        
        for p in products:
            total_bal = 0
            price = 0
            if p.item_code:
                item_price = frappe.get_all('Item Price', fields=['price_list_rate'], filters={'item_code': p.item_code, 'selling': 1}, limit=1, order_by='creation desc')
                if len(item_price) > 0:
                    price = item_price[0].price_list_rate or 0

                balances = get_item_balances(p.item_code)        
                
                if len(balances) > 0:
                    frappe.errprint(p.item_code)
                    item_defaults = frappe.get_all('Item Default', fields=['default_warehouse'], filters={'company': get_company().name, 'parent': p.item_code}, limit=10)

                    for wb in balances:
                        if (wb.warehouse in lookup_warehouses) or (wb.warehouse == item_defaults[0].default_warehouse):
                            total_bal = total_bal + wb.actual_qty
            
            p.update({'price': price})
            p.update({'balance': total_bal})
            
            item_list.append(p)
        
        return item_list
    
    except Exception as e:
        frappe.throw(e)


@frappe.whitelist(allow_guest=True)
def insert_product(data):
    try:
        if isinstance(data, list):
            count = 0
            for p in data:
                check_data(p)
                count += 1
                pd = {'doctype': 'Product'}
                pd.update(p)
                product = frappe.get_doc(pd)
                product = product.insert()

            return 'Inserted {} Products'.format(count)
        elif isinstance(data, dict):
            check_data(data)
            pd = {'doctype': 'Product'}
            pd.update(data)
            product = frappe.get_doc(pd)
            product = product.insert()
            return 'Inserted {}'.format(product.get('sku'))
        else:
            return 'Invalid data type, wrap your JSON object into a list/array like this: {}'.format('''
{
"data": {
        "sku": "SKU407QR",
        "product_name": "Apple",
        "product_category": "Vegetables",
        "processing_type": "Whole",
        "price": 30.0
    }

}''')
    
    except Exception as e:
        return str(e)
    
def check_data(row):
    if 'approved' in map(str.lower, row.keys()):
        frappe.throw(_('Passing a value for "approved" is not allowed'))
    elif 'disable' in map(str.lower, row.keys()):
        frappe.throw(_('Passing a value for "disable" is not allowed'))
    elif 'item_code' in map(str.lower, row.keys()):
        frappe.throw(_('Passing a value for "item_code" is not allowed'))


def get_packhouse_settings():
    return frappe.get_cached_doc('Packhouse Settings', 'Packhouse Settings')