function calc_profit_margin(frm) {
    var selling = frm.doc.standard_rate || 0;
    var cost = frm.doc.valuation_rate || 0;
    if (selling > 0 && cost > 0) {
        var margin = ((selling - cost) / cost) * 100;
        frm.set_value("custom_profit_margin", Math.round(margin * 100) / 100);
    }
}

frappe.ui.form.on("Item", {
    standard_rate: calc_profit_margin,
    valuation_rate: calc_profit_margin,
});
