// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on("Order Request", {
	onload: function(frm){
		frappe.call({
			method: "setup_partner",
			doc: frm.doc,
			callback: () => {
				frm.refresh();
				//refresh_field('items');
			}
		})
	},
	lookup_addr: function(frm){
		lookup_address(frm);
	},
	lookup_customer: function(frm){
		lookup_address(frm);
	}
})

frappe.ui.form.on('Order Request Item', {
	// refresh: function(frm) {

	// }
	
	qty: function(frm) {
		update_totals(frm);		
	},
	price: function(frm) {
		update_totals(frm);		
	},
	item: function(frm) {
		//get_prices(frm);
		update_balances(frm);		
	},
});

function update_totals(frm){
	frappe.call({
		method: "calculate_totals",
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

function lookup_address(frm){
	if ((frm.doc.lookup_addr == '' || frm.doc.lookup_addr == undefined) && (frm.doc.lookup_customer == '' || frm.doc.lookup_customer)){return;}
	frappe.call({
		method: "lookup_address",
		doc: frm.doc,
		callback: () => {
			frm.refresh();
		}
	})
	
}