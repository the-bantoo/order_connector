// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Order Item', {
	// refresh: function(frm) {

	// }
	qty: function(frm) {
		update_totals(frm);		
	},
	price: function(frm) {
		update_totals(frm);		
	},
	item: function(frm) {
		update_balances(frm);		
	},
});

function update_totals(frm){
	frappe.call({
		method: "validate",
		doc: frm.doc,
		callback: () => {
			frm.refresh();
			//refresh_field('items');
		}
	})
}
function update_balances(frm){
	frappe.call({
		method: "update_item_balance",
		doc: frm.doc,
		callback: () => {
			frm.refresh();
		}
	})
}
