from odoo import models, fields, api, _

class BSPaymentExpense(models.Model):
    _name = 'bs.payment.expense'
    _description = 'Payment Expense'

    payment_id = fields.Many2one('account.payment', string=_("Payment"), ondelete='cascade')
    product_id = fields.Many2one('product.product', string=_("Product"), required=True)
    total_amount = fields.Float(string="Total Amount", required=True)
    department_id = fields.Many2one('hr.department', string=_("Department"))
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"))
    name = fields.Char(string=_("Name"), required=True)


class ProductProduct(models.Model):
    _inherit = 'product.template'

    department_id = fields.Many2one('hr.department', string=_("Department"), help="Department associated with the product.")
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"), help="Cost item associated with the product.")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    expense_ids = fields.One2many(
        'bs.payment.expense', 'payment_id', string=_("Expenses")
    )

    @api.model_create_multi
    def create(self, vals_list):
        payments = super(AccountPayment, self).create(vals_list)
        for payment in payments:
            payment._populate_expenses()
        return payments

    def _populate_expenses(self):
        """ Populate expenses from invoice lines into the payment, either proportional or total. """
        for payment in self:
            if payment.reconciled_invoice_ids:  # Invoices linked to the payment
                for invoice in payment.reconciled_invoice_ids:
                    for line in invoice.invoice_line_ids:

                        if invoice.amount_total > 0:
                            proportion = line.price_subtotal / invoice.amount_total  # Proportional amount
                            expense_amount = proportion * payment.amount  # Portion of the payment
                        else:
                            expense_amount = line.price_subtotal  # If no total amount, use the full amount of the line


                        self.env['bs.payment.expense'].create({
                            'payment_id': payment.id,
                            'product_id': line.product_id.id,
                            'total_amount': expense_amount,
                            'department_id': line.department_id.id,  # Заміна з line.product_id.department_id
                            'cost_item_id': line.cost_item_id.id,  # Заміна з line.product_id.cost_item_id
                            'name': line.name,
                        })

    def action_populate_expenses(self):
        """ Manual population of expenses. """
        self.ensure_one()
        self._populate_expenses()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    department_id = fields.Many2one(
        'hr.department',
        string=_("Department"),
        help="Department linked to this line.",
        readonly=False,
        tracking=True
    )
    cost_item_id = fields.Many2one(
        'bs.cost.item',
        string=_("Cost Item"),
        help="Cost item linked to this line.",
        readonly=False,
        tracking=True
    )

