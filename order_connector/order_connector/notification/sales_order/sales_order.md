<h3>Order Summary</h3>

<table border=2 >
    <tr align="center">
        <th>Item</th>
        <th>Quantity</th>
        <th>Unit</th>
    </tr>
    {% for item in doc.items %}
        {% if frappe.utils.flt(item.received_qty, 2) > 0.0 %}
            <tr align="center">
                <td>{{ item.item_code }}</td>
                <td>{{ frappe.utils.flt(item.qty, 2) }}</td>
                <td>{{ item.uom }}</td>
            </tr>
        {% endif %}
    {% endfor %}
</table>

<center><button class='btn-primary btn-lg primary-action' href='{{ frappe.utils.get_url_to_form("Sales Order", doc.name) }}'>Open Order</button></center>

