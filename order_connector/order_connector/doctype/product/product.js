// Copyright (c) 2023, Bantoo and contributors
// For license information, please see license.txt

frappe.ui.form.on('Product', {
	refresh: function(frm) {
		// frm.refresh_field('connection_status');
		update_status(frm)
	},
	save: function(frm) {
		frm.refresh();
	}
});

function update_status(frm) {
	frm.dashboard.clear_comment();
	if (!frm.doc.product_name || !frm.doc.item_code){
		frm.dashboard.add_comment(__("Complete the form and select a matching Item to activate"), "blue", true);
	}
	else if (frm.doc.disabled === 0 && frm.doc.item_code){
		frm.dashboard.add_comment(__("Active"), "green", true);
		console.table('active')
	}
	else {
		frm.dashboard.add_comment(__("Disabled"), "red", true);
	}
}
