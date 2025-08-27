# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    branch_id = fields.Many2one(
        'res.company',  # Could be changed to your branch model if available
        string='Branch',
        required=True
    )
    vendor_assigned_ids = fields.One2many(
        'purchase.vendor.line',  # Make sure this model exists
        'order_id',
        string="Vendor Assignments",
    )
    approval_state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('to_approve', 'To Approve'),
            ('gm_approved', 'GM Approved'),
            ('level1_approved', 'Level 1 Approved'),
            ('level2_approved', 'Level 2 Approved'),
        ],
        string='Approval State',
        default='draft',
        readonly=True,
        copy=False
    )

    def action_initiate_request(self):
        """Purchase Creator initiates the request"""
        for rec in self:
            if rec.approval_state != 'draft':
                continue
            rec.approval_state = 'to_approve'
            rec.message_post(body="Purchase request initiated by branch.")

    def action_gm_approve(self):
        """General Manager approves product-wise"""
        for order in self:
            if order.approval_state != 'to_approve':
                continue
            # Check that all lines have GM vendor assigned
            unassigned_lines = order.order_line.filtered(lambda l: not l.gm_vendor_id)
            if unassigned_lines:
                products = ", ".join(unassigned_lines.mapped("product_id.name"))
                raise UserError(f"Please assign GM vendors for all products: {products}")
            order.approval_state = 'gm_approved'
            order.message_post(body="GM approved. Order moved to Level 1 Approval.")

    def action_level1_approve(self):
        """Level 1 approval"""
        for rec in self:
            if rec.approval_state != 'gm_approved':
                continue
            rec.approval_state = 'level1_approved'
            rec.message_post(body="Level 1 approval granted.")

    def action_level2_approve(self):
        """Level 2 Final Approval"""
        for rec in self:
            if rec.approval_state != 'level1_approved':
                continue
            rec.approval_state = 'level2_approved'
            rec.button_confirm()
            rec.message_post(body="Level 2 approval granted. PO confirmed.")


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    branch_id = fields.Many2one(
        'res.company',
        related='order_id.branch_id',
        store=True,
        readonly=True,
        string='Branch'
    )
    gm_vendor_id = fields.Many2one(
        'res.partner',
        string='GM Assigned Vendor',
        domain=[('supplier_rank', '>', 0)]
    )
    vendor_id_display = fields.Many2one(
        'res.partner',
        compute='_compute_vendor_display',
        string='Vendor',
        store=False
    )

    @api.depends('gm_vendor_id', 'order_id.partner_id')
    def _compute_vendor_display(self):
        for rec in self:
            rec.vendor_id_display = rec.gm_vendor_id or rec.order_id.partner_id

    @api.onchange('product_id')
    def _onchange_product_limit_gm_vendor(self):
        for rec in self:
            if not rec.product_id:
                continue
            sellers = rec.product_id.seller_ids.mapped('partner_id')
            if sellers:
                return {'domain': {'gm_vendor_id': [('id', 'in', sellers.ids)]}}
            return {'domain': {'gm_vendor_id': [('supplier_rank', '>', 0)]}}

    @api.constrains('gm_vendor_id', 'product_qty')
    def _check_vendor_and_qty(self):
        for rec in self:
            if rec.gm_vendor_id and rec.gm_vendor_id.supplier_rank <= 0:
                raise ValidationError("Selected GM vendor is not a supplier.")
            if rec.product_qty <= 0:
                raise ValidationError("Quantity must be greater than zero.")

    def action_gm_approve_from_line(self):
        """Approve the related purchase orders from line view"""
        orders = self.mapped('order_id')
        for order in orders:
            order.action_gm_approve()
