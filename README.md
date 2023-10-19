## Order Connector

Simplifies order placement from third-parties

### Usage
Examples are provided using Javascript, but you can use any language and simply make an http request to the server.

First, you'll need an active host, an api_key and api_secret like so:

```
const host = 'http://127.0.0.1';
const api_key = '22dd9b699b04551';
const api_secret = 'b56e27e7f065abf';
```

#### Getting Items: GET - /api/method/order_connector.api.get_items
```JavaScript
const url = new URL(host + "/api/method/order_connector.api.get_items");
url.searchParams.set("item_code", "Onion Kg"); // optional: limit to specified item
//url.searchParams.set("limit", "1"); // optional: limit to one result

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

#### Getting Orders: GET - /api/method/order_connector.api.get_orders
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

#### Inserting Orders: POST - /api/method/order_connector.api.insert_order

```JavaScript
const url = new URL(host + "/api/method/order_connector.api.insert_order");
const data = JSON.stringify({
    "data": {
        "delivery_date": "2023-10-18",
        "partner_order_no": "Test",
        "customer": "Test",
        "customer_address": "Test",
        "items": [
            {
                "item_name": "Beans",
                "unit": "Kg",
                "qty": 1,
                "price": 10
            }
        ]
    }
});

fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `token ${api_key}:${api_secret}`
    },
    body: data
}).then(response => {
    return response.json();
}).then(data => {
    console.log(data.message);
});
```

#### License

MIT
