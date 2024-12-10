from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class BSPaymentExpense(models.Model):
    _name = 'bs.payment.expense'
    _description = 'Payment Expense'

    payment_id = fields.Many2one('account.payment', string=_("Payment"), ondelete='cascade')
    product_id = fields.Many2one('product.product', string=_("Product"), required=True)
    total_amount = fields.Float(string=_("Total Amount"), required=True)
    department_id = fields.Many2one('hr.department', string=_("Department"))
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"))
    label = fields.Char(string=_("Label"), required=True)



class ProductProduct(models.Model):
    _inherit = 'product.template'

    department_id = fields.Many2one('hr.department', string=_("Department"), help="Department associated with the product.")
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"), help="Cost item associated with the product.")


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    expense_ids = fields.One2many(
        'bs.payment.expense', 'payment_id', string=_("Expenses")
    )

    def action_post(self):
        """When the payment is posted, create expense entries."""
        result = super(AccountPayment, self).action_post()
        for payment in self:
            if payment.partner_type == 'supplier':  # Only for supplier payments
                payment._populate_expenses()
                payment._create_expense_entries()
        return result

    def button_draft(self):
        """When the payment is set to draft, delete related expense entries."""
        for payment in self:
            if payment.partner_type == 'supplier':  # Only for supplier payments
                payment.expense_ids.unlink()  # Delete expense records
                payment._delete_expense_entries()
        return super(AccountPayment, self).button_draft()

    @api.model_create_multi
    def create(self, vals_list):
        """Automatically populate expenses during payment creation."""
        payments = super(AccountPayment, self).create(vals_list)
        for payment in payments:
            if payment.partner_type == 'supplier':  # Only for supplier payments
                payment._populate_expenses()
        return payments

    def write(self, vals):
        """Automatically update expenses when the payment amount or reconciled invoices change."""
        res = super(AccountPayment, self).write(vals)
        for payment in self:
            if 'amount' in vals or 'reconciled_invoice_ids' in vals:
                if payment.partner_type == 'supplier':  # Only for supplier payments
                    payment._populate_expenses()
        return res

    def action_populate_expenses(self):
        """Manual expense population, available only for supplier payments."""
        for payment in self:
            if payment.partner_type == 'supplier':  # Only for supplier payments
                payment._populate_expenses()

    def _populate_expenses(self):
        """Populate expenses from supplier invoices into payment."""
        for payment in self:
            if payment.partner_type != 'supplier':  # Skip if not supplier payment
                continue

            payment.expense_ids.unlink()  # Clear previous expenses

            invoices = payment.reconciled_invoice_ids
            if not invoices:
                continue  # Skip if no invoices are found

            # Populate expenses based on invoice lines
            for invoice in invoices:
                for line in invoice.invoice_line_ids:
                    expense_amount = 0
                    if invoice.amount_total > 0:
                        proportion = line.price_subtotal / invoice.amount_total
                        expense_amount = proportion * payment.amount
                    else:
                        expense_amount = line.price_subtotal

                    # Create expense record
                    self.env['bs.payment.expense'].create({
                        'payment_id': payment.id,
                        'product_id': line.product_id.id,
                        'total_amount': expense_amount,
                        'department_id': line.department_id.id if line.department_id else False,
                        'cost_item_id': line.cost_item_id.id if line.cost_item_id else False,
                        'label': line.name or _('No Label'),
                    })

    def _create_expense_entries(self):
        """Create detailed expense entries in `bs.payment.expense.entry`."""
        for payment in self:
            entries = []
            for invoice in payment.reconciled_invoice_ids:
                for line in invoice.invoice_line_ids:
                    if line.cost_item_id and line.cost_item_id.allocate_to_departments:
                        for department in line.cost_item_id.department_ids:
                            allocated_amount = (line.price_subtotal * department.percentage) / 100
                            entries.append({
                                'account_payment_id': payment.id,
                                'date': fields.Datetime.now(),
                                'department_id': department.department_id.id,
                                'cost_item_id': line.cost_item_id.id,
                                'amount': allocated_amount,
                            })
                    else:
                        entries.append({
                            'account_payment_id': payment.id,
                            'date': fields.Datetime.now(),
                            'department_id': line.department_id.id,
                            'cost_item_id': line.cost_item_id.id,
                            'amount': line.price_subtotal,
                        })
            # Bulk create entries
            if entries:
                self.env['bs.payment.expense.entry'].create(entries)

    def _delete_expense_entries(self):
        """Delete all expense entries related to the payment."""
        self.env['bs.payment.expense.entry'].search([
            ('account_payment_id', '=', self.id)
        ]).unlink()










