from odoo import models, fields, api, _


class BSPaymentExpenseEntry(models.Model):
    _name = 'bs.payment.expense.entry'
    _description = 'Payment Expense Entry'

    account_payment_id = fields.Many2one('account.payment', string=_("Payment"), ondelete='cascade')
    date = fields.Datetime(string=_("Date"), required=True)
    department_id = fields.Many2one('hr.department', string=_("Department"))
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"))
    amount = fields.Float(string="Amount")

