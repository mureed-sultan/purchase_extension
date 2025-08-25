# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    vendor_assigned_ids = fields.One2many(
        "purchase.vendor.line",
        "order_id",
        string="Vendor Assignments",
    )

    approval_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("to_approve", "To Approve"),
            ("gm_approved", "GM Approved"),
            ("level1_approved", "Level 1 Approved"),
            ("level2_approved", "Level 2 Approved"),
        ],
        string="Approval State",
        default="draft",
        readonly=True,
        copy=False,
    )

    # NOTE: we use the standard partner_id (vendor) field on purchase.order
    # partner_id stays as-is; we only hide/show it in the view.

    def action_initiate_request(self):
        for rec in self:
            if rec.approval_state == "draft":
                rec.approval_state = "to_approve"
                rec.message_post(body="Purchase request initiated by branch.")

    def action_gm_approve(self):
        """GM must approve - ensure vendor is assigned before approving.

        Rules:
        - If partner_id is set -> ok.
        - Else if vendor_assigned_ids contains exactly one unique vendor -> auto-copy it to partner_id and continue.
        - Else -> raise error asking GM to assign vendor.
        """
        for order in self:
            if order.approval_state != "to_approve":
                # Not in correct state — ignore or optionally raise
                continue

            # If partner (vendor) already set, proceed
            if order.partner_id:
                order.approval_state = "gm_approved"
                order.message_post(body="General Manager approved the order.")
                continue

            # Try to infer vendor from vendor_assigned_ids (only if exactly one unique vendor)
            vendor_ids = {line.vendor_id.id for line in order.vendor_assigned_ids if line.vendor_id}
            if len(vendor_ids) == 1:
                vendor_id = vendor_ids.pop()
                order.partner_id = vendor_id
                order.approval_state = "gm_approved"
                order.message_post(body="General Manager approved the order (vendor auto-copied).")
                continue

            # Nothing set; require GM to choose a vendor
            raise UserError(_("General Manager must assign a Vendor before approval."))

    def action_level1_approve(self):
        for rec in self:
            if rec.approval_state == "gm_approved":
                rec.approval_state = "level1_approved"
                rec.message_post(body="Level 1 approval granted.")

    def action_level2_approve(self):
        for rec in self:
            if rec.approval_state == "level1_approved":
                rec.approval_state = "level2_approved"
                # Confirm the PO using standard Odoo method
                rec.button_confirm()
                rec.message_post(body="Level 2 approval granted and purchase order confirmed.")

    def action_print_demand(self):
        return self.env.ref("purchase.purchase_order_report").report_action(self)
