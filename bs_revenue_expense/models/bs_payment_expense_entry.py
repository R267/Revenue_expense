from odoo import models, fields, api, _

class BSPaymentExpenseEntry(models.Model):
    _name = 'bs.payment.expense.entry'
    _description = 'Payment Expense Entry'

    account_payment_id = fields.Many2one('account.payment', string=_("Payment"), ondelete='cascade')
    date = fields.Datetime(string=_("Date"), required=True)
    department_id = fields.Many2one('hr.department', string=_("Department"))
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"))
    amount = fields.Float(string="Amount")

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        """When payment moves to 'posted', create expense entries."""
        result = super(AccountPayment, self).action_post()
        for payment in self:
            payment._create_expense_entries()
        return result

    def button_draft(self):
        """When payment moves to 'draft', delete related expense entries."""
        for payment in self:
            payment._delete_expense_entries()
        return super(AccountPayment, self).button_draft()

    def _create_expense_entries(self):
        """Create entries in bs.payment.expense.entry based on invoice lines."""
        for payment in self:
            entries = []
            for invoice in payment.reconciled_invoice_ids:
                for line in invoice.invoice_line_ids:
                    cost_item = line.cost_item_id
                    if cost_item and cost_item.allocate_to_departments:
                        # Distribute amount across departments based on percentages
                        for department in cost_item.department_ids:
                            allocated_amount = (line.price_subtotal * department.percent) / 100
                            entries.append({
                                'account_payment_id': payment.id,
                                'date': fields.Datetime.now(),
                                'department_id': department.department_id.id,
                                'cost_item_id': cost_item.id,
                                'amount': allocated_amount,
                            })
                    else:
                        # Standard entry without distribution
                        entries.append({
                            'account_payment_id': payment.id,
                            'date': fields.Datetime.now(),
                            'department_id': line.department_id.id,
                            'cost_item_id': line.cost_item_id.id,
                            'amount': line.price_subtotal,
                        })
            # Bulk create entries
            self.env['bs.payment.expense.entry'].create(entries)

    def _delete_expense_entries(self):
        """Delete all expense entries related to the payment."""
        self.env['bs.payment.expense.entry'].search([
            ('account_payment_id', '=', self.id)
        ]).unlink()