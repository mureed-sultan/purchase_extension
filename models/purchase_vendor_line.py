# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError

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
        domain=[("supplier_rank", ">", 0)],
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
    )
    # branch shown using company-as-branch
    branch_id = fields.Many2one(
        "res.company",
        string="Branch",
        related="order_id.branch_id",
        store=True,
        readonly=True,
    )

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.product_id and self.product_id.seller_ids:
            self.vendor_id = self.product_id.seller_ids[0].name

    @api.constrains('quantity')
    def _check_qty(self):
        for rec in self:
            if rec.quantity <= 0:
                raise ValidationError("Quantity must be greater than zero.")
