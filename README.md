# Order Connector

#### Simplifies order placement from third-parties into ERPNext for Farmers Den

1. [Getting Products](#1)
2. [Inserting Products](#2)
3. [Getting Orders](#3)
4. [Inserting Orders](#4)

#### [Need help / support?](#support)

#### Todo (coming soon)
- Update Orders
- Update Products

---

## Usage
Examples are provided using Javascript and python, but you can use any language and simply make an http request to the server.

First, you'll need an active `host`, an `api_key` and `api_secret` like so:

```
const host = 'http://127.0.0.1';
const api_key = '22dd9b699b04551';
const api_secret = 'b56e27e7f065abf';
```
---

### <a name="1"></a>1. Getting Products: GET - get_products

#### Endpoint: `{{host}}/api/method/order_connector.api.get_products`

#### Parameters

| Parameter | Type   | Description                                  | Default Value | Mandatory |
|-----------|--------|----------------------------------------------|---------------|-----------|
| `sku`     | string | The Stock Keeping Unit (SKU) of the product. | null            | No        |
| `limit`   | integer| The maximum number of products to retrieve.  | 20            | No        |

#### Response

The API returns a list of products with the following fields:

| Field Name       | Type    | Description                                      |
|------------------|---------|--------------------------------------------------|
| `sku`            | string  | Stock Keeping Unit (SKU) of the product.         |
| `product_name`   | string  | Name of the product.                             |
| `description`    | string  | Description of the product.                      |
| `product_category`| string | Category of the product.                         |
| `processing_type`| string  | Type of processing for the product.              |
| `item_code`      | string  | Farmers Den's Stock Item code associated with the product.           |
| `unit`    | float    | Unit of Measure of, e.g Kg, Litre, Meter, Each, etc. | Yes      |
| `approved`       | integer | Approval status of the product. 1= True / 0 = False                 |
| `disabled`       | integer | Disabled status of the product. 1= True / 0 = False                  |
| `price`          | float   | Price of the product (if applicable).            |
| `balance`        | float   | Total balance of the product in warehouses.      |


#### Example Request (JavaScript)

```JavaScript
const url = new URL(host + "/api/method/order_connector.api.get_products");
//url.searchParams.set("sku", "SKU123"); // optional: limit to specified sku
url.searchParams.set("limit", "1"); // optional: limit to one result

fetch(url, {
    method: "GET",
    headers: {
    "Content-Type": "application/json",
    "Authorization": `token ${api_key}:${api_secret}`
    }
}).then(response => {
    return response.json();
}).then(data => {
    console.log(data.message);
});
```

#### Python Example
```python
    url = '{}/api/method/order_connector.api.get_products'.format(host)
    params = {
        "sku": "",
        "limit": 2
    }
    # params = {} // no params option or any params

    try:
        response = requests.get(url, json=params, headers={'Authorization': 'token {}:{}'.format(api_key, api_secret)})

        if response.status_code == 200:
            products = response.json()
            print(products)
        else:
            print(f"Error: {response.status_code}: {response.status_message}")
    except Exception as e: 
        print(e)
```

#### Example Response

```json
[
    {
        "sku": "SKU161EG",
        "product_name": "Cabbage (Chinese)",
        "description": null,
        "product_category": "Vegetables",
        "processing_type": "Chopped",
        "taxable": 0,
        "unit": "Kg",
        "item_code": null,
        "approved": 0,
        "disabled": 0,
        "price": 0,
        "balance": 0
    }
]
```

---

## <a name="2"></a>2. Inserting Products: GET - insert_product
#### Endpoint: `{{host}}/api/method/order_connector.api/insert_product`

Allows for a single or bulk insertion of products.

#### Parameters

| Parameter | Type   | Description                                            | Mandatory |
|-----------|--------|--------------------------------------------------------|-----------|
| `data`    | object | JSON object containing product details. See examples below. | Yes       |

| Parameter         | Type     | Description                                         | Mandatory |
|-------------------|----------|-----------------------------------------------------|-----------|
| `sku`             | string   | Stock Keeping Unit/ID of the product.               | Yes       |
| `product_name`    | string   | Name of the product.                                | Yes       |
| `product_category`| string   | Category of the product.                            | Yes       |
| `processing_type` | string   | Type of processing for the product.                 | Yes       |
| `taxable`         | int      | 1 for Yes, 0 for No.                                | Yes       |
| `price`           | float    | Price of the product.                               | No        |
| `unit`            | float    | Unit of Measure of, e.g Kg, Litre, Meter, Each, etc. | Yes      |

#### Request Body Example (Inserting a Single Product)

```json
{
    "data": {
        "sku": "SKU407QR",
        "product_name": "Apple",
        "product_category": "Vegetables",
        "processing_type": "Whole",
        "taxable": 0,
        "unit": "Kg",
        "price": 30.0
    }
}
```
or

```json
{
    "data": [
        {
            "sku": "SKU407QR",
            "product_name": "Apple",
            "product_category": "Vegetables",
            "taxable": 0,
            "unit": "Kg",
            "processing_type": "Whole"
        }
    ]
}
``` 


#### Request Body Example (Inserting Multiple Products)

```json
{
    "data": [
        {
            "sku": "SKU407QR",
            "product_name": "Apple",
            "product_category": "Vegetables",
            "processing_type": "Whole",
            "taxable": 0,
            "unit": "Kg",
            "price": 30.0
        },
        {
            "sku": "SKU123AB",
            "product_name": "Banana",
            "product_category": "Fruits",
            "processing_type": "Whole",
            "taxable": 0,
            "unit": "Kg"
        }
    ]
}
```

#### Example Request (JavaScript)

```JavaScript
const url = new URL('{{host}}/api/method/order_connector.api.insert_product');

fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Authorization": `token {{api_key}}:{{api_secret}}`
    },
    body: JSON.stringify({
        "data": {
            "sku": "SKU407QR",
            "product_name": "Apple",
            "product_category": "Vegetables",
            "processing_type": "Whole",
            "taxable": 0,
            "unit": "Kg",
            "price": 30.0
        }
    })
}).then(response => {
    return response.json();
}).then(data => {
    console.log(data.message);
});
```

#### Response Example

The API returns a message indicating the success of the operation.

For single product insertion:

```JSON
{
    "message": "Inserted SKU407QR"
}
```

For multiple product insertion:

```JSON
{
    "message": "Inserted 2 Products"
}
```

#### Example Request (Python)

```python
import requests

url = host + '/api/method/order_connector.api.insert_product'
params = {
    "data": [
        {
            "sku": "SKU407QR",
            "product_name": "Apple",
            "product_category": "Vegetables",
            "processing_type": "Whole"
            "unit": "Kg",
        },        
        {
            "sku": "SKU407Q2",
            "product_name": "Apple",
            "product_category": "Vegetables",
            "processing_type": "Whole",
            "unit": "Kg",
            "price": 30.0
        },
        
    ]
}

response = requests.post(url, json=params, headers={'Authorization': 'Bearer YOUR_TOKEN'})

if response.status_code == 200:
    product_name = response.json()
    print(f"Inserted product: {product_name}")
else:
    print(f"Error: {response.status_code}")
```

---

## <a name="3"></a>3. Getting Orders: GET - get_orders
### Endpoint: `{{host}}/api/method/order_connector.api.get_orders`

### Parameters

| Parameter | Type     | Description                            | Default Value | Mandatory     |
|-----------|----------|----------------------------------------|---------------|---------------|
| `name`    | string   | The name of the order request.         | null            | No            |
| `limit`   | integer  | The maximum number of order requests.  | 20             | No            |

### Response

The API returns a list of order requests with the following fields:

| Field Name        | Type    | Description                                      |
|-------------------|---------|--------------------------------------------------|
| `name`            | string  | The name of the order.                   |
| `partner_order_no`| string  | Partner's order number.                          |
| `customer`        | string  | Customer's name.                                |
| `customer_address`| string  | Customer's address.                             |
| `gps_coordinates`| string  | Customer's GPS Location.                             |
| `total_amount`    | float   | Total amount of the order.               |
| `status`          | string  | Current status of the order.             |
| `docstatus`       | integer | Document status.                                |
| `remarks`         | string  | Additional remarks.                             |
| `creation`        | date    | Creation date of the order.              |
| `modified`        | date    | Last modified date of the order.         |
| `owner`           | string  | Creator of the order.                      |
| `items`           | list    | List of items in the order, each containing: |
|                   |         | - `sku`: Stock Keeping Unit/ID of the item.                 |
|                   |         | - `processing_type`: SKU processing type        |
|                   |         | - `description`: Description of the item.        |
|                   |         | - `unit`: Unit of measurement.                   |
|                   |         | - `qty`: Quantity of the item.                   |
|                   |         | - `price`: Price of the item.                    |
|                   |         | - `amount`: Total amount for the item.           |
|                   |         | - `status`: Order status for the item. Possible states:|
|                   |         | [`Pending`, `Completed`, `Rejected`, `Cancelled`] |


### Example Response

```json
[
    {
        "name": "OR-0001",
        "partner_order_no": "PO-123",
        "customer": "John Doe",
        "gps_coordinates": "1,1",
        "customer_address": "123 Main Street",
        "total_amount": 500.00,
        "status": "Accepted",
        "docstatus": 1,
        "remarks": "Urgent order",
        "creation": "2023-11-08",
        "modified": "2023-11-09",
        "owner": "admin",
        "items": [
            {
                "item_name": "Item A",
                "description": "Description of Item A",
                "unit": "pcs",
                "qty": 10,
                "price": 50.00,
                "amount": 500.00
            }
        ]
    }
]
```

### Example Request (JavaScript)

```JavaScript
const url = new URL(host + "/api/method/order_connector.api.get_orders");
//url.searchParams.set("name", "ORD-181023-0014"); // optional: limit to specified order
url.searchParams.set("limit", "2"); // optional: limit to one result

fetch(url, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `token ${api_key}:${api_secret}`
    }
}).then(response => {
    return response.json();
}).then(data => {
    console.log(data.message);
});
```

### Example Request (Python)

```python
import requests

host = 'http://localhost:8000'
api_key = 'xxxxx'
api_secret = 'xxxxxx'
url = '{}/api/method/order_connector.api.get_orders'.format(host)
#params = {
#    "name": "ORD-071123-0017",
#    "limit": 2
#}
params = {}

try:
    response = requests.get(url, json=params, headers={'Authorization': 'token {}:{}'.format(api_key, api_secret)})

    if response.status_code == 200:
        orders = response.json()
        print(orders)
    else:
        print(f"Error: {response.status_code}: {response.status_message}")
except Exception as e: 
    print(e)
```

---

## <a name="4"></a>4. Inserting Orders: POST - insert_order
#### Endpoint: `{{host}}/api/method/order_connector.api/insert_order`

#### Parameters

| Parameter | Type   | Description                                      | Mandatory |
|-----------|--------|--------------------------------------------------|-----------|
| `data`    | object | JSON object containing order details. See example below. | Yes       |

| Parameter         | Type     | Description                                    | Mandatory |
|-------------------|----------|------------------------------------------------|-----------|
| `order_date`      | string   | The date of the order. Format: "YYYY-MM-DD"    | Yes       |
| `delivery_date`   | string   | The delivery date of the order. Format: "YYYY-MM-DD" | Yes |
| `partner_order_no`| string   | Partner's order number.                        | Yes       |
| `customer`        | string   | Customer's name.                               | Yes       |
| `customer_address`| string   | Customer's address.                            | Yes       |
| `gps_coordinates` | string   | Customer's GPS Location.                       | No        |
| `email`           | string   | Customer's email address.                      | No        |
| `phone_number`    | string   | Customer's phone number.                       | No        |
| `remarks`         | string   | Additional remarks or notes.                   | No        |
| `items`         | list   | Order items, detailed in the table below           | Yes       |

##### Item List Details

| Parameter  | Type     | Description                                      | Mandatory |
|------------|----------|--------------------------------------------------|-----------|
| `sku`      | string   | Stock Keeping Unit/ID of the item.               | Yes       |
| `unit`     | string   | Unit of measurement for the item.                | Yes       |
| `qty`      | float    | Quantity of the item.                            | Yes       |
| `price`    | float    | Price of the item. Only required if there's a price change. | No        |

#### Request Body Example
```json
"data": {
    "order_date": "2023-10-18",
    "delivery_date": "2023-10-18",
    "partner_order_no": "Test",
    "customer": "Test",
    "customer_address": "Test",
    "gps_coordinates": "1,1",
    "email": "email@test.com",
    "phone_number": "123",
    "remarks": "Test",
    "items": [
        {
            "sku": "SKU316DE",
            "unit": "Kg",
            "qty": 1.0,
            "price": 10.0
        }
    ]
}
```

#### Example Request (JavaScript)

```JavaScript
const url = new URL(host + "/api/method/order_connector.api.insert_order");

fetch(url, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "Authorization": `token ${api_key}:${api_secret}`
    },
    body: JSON.stringify({
        "data": {
            "order_date": "2023-10-18",
            "delivery_date": "2023-10-18",
            "partner_order_no": "Test",
            "customer": "Test",
            "gps_coordinates": "1,1",
            "customer_address": "123 Main Street",
            "email": "email@test.com",
            "phone_number": "123",
            "remarks": "Test",
            "items": [
                {
                    "sku": "SKU316DE",
                    "unit": "Kg",
                    "qty": 1.0,
                    "price": 10.0
                }
            ]
        }
    })
}).then(response => {
    return response.json();
}).then(data => {
    console.log(data.message);
});
```

#### Response

The API returns the name of the inserted order.
```JSON
{
    "message": "ORD-081123-0030"
}
```

#### Example Request (Python)

```python
url = '{}/api/method/order_connector.api.insert_order'.format(host)
params = {
    "data": {
        "order_date": "2023-10-18",
        "delivery_date": "2023-10-18",
        "partner_order_no": "Test",
        "customer": "Test",
        "customer_address": "Test",
        "gps_coordinates": "1,1",
        "email": "email@test.com",
        "phone_number": "123",
        "remarks": "Test",
        "items": [
            {
                "sku": "SKU316DE",
                "unit": "Kg",
                "qty": 1.0,
                "price": 10.0
            }
        ]
    }
}



try:
    response = requests.get(url, json=params, headers={'Authorization': 'token {}:{}'.format(api_key, api_secret)})

    if response.status_code == 200:
        order_name = response.json()
        print(f"Inserted order: {order_name}")
    else:
        print(f"Error: {response.status_code}: {response.status_message}")
except Exception as e: 
    print(e)
```


#### Response

The API returns the name of the inserted order.
```JSON
{
    "message": "ORD-081123-0030"
}
```

---

## <a name="support"></a> Need help?
- Telegram: https://t.me/dee_adam
- email: devs@thebantoo.com

---


#### License

MIT
