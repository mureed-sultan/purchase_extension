from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Branch/Warehouse that will receive the goods (you can map to your “branch” concept)
    branch_id = fields.Many2one("stock.warehouse", string="Branch / Warehouse")

    initiated_by = fields.Many2one(
        "res.users", string="Initiated By", default=lambda self: self.env.user, readonly=True
    )

    # Two-level approval workflow
    approval_state = fields.Selection([
        ("draft", "Draft"),
        ("initiated", "Initiated"),
        ("waiting_l1", "Waiting L1 Approval"),
        ("waiting_l2", "Waiting L2 Approval"),
        ("approved", "Approved"),
    ], string="Request State", default="draft", tracking=True)

    # Column visibility toggles (default disabled)
    show_unit_price = fields.Boolean("Show Unit Price", default=False)
    show_amounts = fields.Boolean("Show Amounts", default=False)
    show_taxes = fields.Boolean("Show Taxes", default=False)

    # Make vendor optional (relaxes the base field)
    partner_id = fields.Many2one(required=False)

    # Ask confirmation (receipt reminder): default checked
    receipt_reminder_email = fields.Boolean(default=True)

    # ----- Workflow buttons -----
    def action_initiate(self):
        for order in self:
            order.approval_state = "initiated"
            if not order.initiated_by:
                order.initiated_by = self.env.user
            order.message_post(body=_("Purchase Request initiated by %s.") % self.env.user.name)
        return self._return_action_open()

    def action_send_for_approval(self):
        for order in self:
            if order.approval_state not in ("initiated", "draft"):
                continue
            order.approval_state = "waiting_l1"
            order.message_post(body=_("Request sent for Level 1 approval."))
        return self._return_action_open()

    def action_approve_level1(self):
        self._check_has_group("purchase_extension.group_purchase_approver_l1")
        for order in self:
            if order.approval_state != "waiting_l1":
                continue
            order.approval_state = "waiting_l2"
            order.message_post(body=_("Approved by Level 1. Waiting Level 2 approval."))
        return self._return_action_open()

    def action_approve_level2(self):
        self._check_has_group("purchase_extension.group_purchase_approver_l2")
        for order in self:
            if order.approval_state != "waiting_l2":
                continue
            order.approval_state = "approved"
            order.message_post(body=_("Approved by Level 2. You can confirm the PO."))
        return self._return_action_open()

    def _check_has_group(self, xmlid):
        if not self.env.user.has_group(xmlid):
            raise UserError(_("You don't have permission to perform this action."))

    def _return_action_open(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    # Require L2 approval before confirming PO
    def button_confirm(self):
        for order in self:
            if order.approval_state != "approved":
                raise UserError(_("This PO requires Level 2 approval before confirm."))
        return super().button_confirm()
