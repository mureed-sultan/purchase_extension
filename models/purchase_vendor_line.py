# -*- coding: utf-8 -*-
from odoo import models, fields

class PurchaseVendorLine(models.Model):
    _name = "purchase.vendor.line"
    _description = "Vendor Assignment Line"
    _rec_name = "vendor_id"

    order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order",
        required=True,
        ondelete="cascade",
        index=True,
    )
    product_id = fields.Many2one(
        "product.product",
        string="Product",
        required=True,
    )
    vendor_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        required=True,
        domain=[("supplier_rank", ">", 0)],
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
    )
