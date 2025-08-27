# -*- coding: utf-8 -*-
from odoo import models, fields

class PurchaseGMAssignment(models.Model):
    _name = "purchase.gm.assignment"
    _description = "GM Product Assignment"

    order_id = fields.Many2one("purchase.order", string="Purchase Order", ondelete="cascade")
    branch_id = fields.Many2one("res.company", string="Branch")
    product_id = fields.Many2one("product.product", string="Product")
    vendor_id = fields.Many2one("res.partner", string="Vendor", domain=[('supplier_rank', '>', 0)])
    quantity = fields.Float(string="Quantity", default=0.0)
