from odoo import models, fields, api, _
from odoo.exceptions import UserError

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

    @api.model_create_multi
    def create(self, vals_list):
        """ Автоматично заповнює витрати під час створення платежу. """
        payments = super(AccountPayment, self).create(vals_list)
        for payment in payments:
            payment._populate_expenses()
        return payments

    def write(self, vals):
        """ Автоматично оновлює витрати при зміні суми платежу або рахунка. """
        res = super(AccountPayment, self).write(vals)
        if 'amount' in vals or 'reconciled_invoice_ids' in vals:
            self._populate_expenses()
        return res

    def _populate_expenses(self):
        """ Заповнює витрати з рядків рахунка у платіж. """
        for payment in self:
            payment.expense_ids.unlink()  # Очистити попередні записи витрат
            if payment.reconciled_invoice_ids:  # Перевірка, чи пов’язаний рахунок
                for invoice in payment.reconciled_invoice_ids:
                    for line in invoice.invoice_line_ids:
                        if invoice.amount_total > 0:
                            proportion = line.price_subtotal / invoice.amount_total  # Пропорційна сума
                            expense_amount = proportion * payment.amount  # Частина платежу
                        else:
                            expense_amount = line.price_subtotal  # Використати повну суму рядка

                        # Створення запису в моделі витрат
                        self.env['bs.payment.expense'].create({
                            'payment_id': payment.id,
                            'product_id': line.product_id.id,
                            'total_amount': expense_amount,
                            'department_id': line.department_id.id,  # Використовує department_id із рядка
                            'cost_item_id': line.cost_item_id.id,  # Використовує cost_item_id із рядка
                            'label': line.name or _('No Label'),
                        })

    def action_populate_expenses(self):
        """ Заповнення витрат вручну через кнопку. """
        self.ensure_one()  # Переконатися, що викликається лише для одного запису
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

class AccountMove(models.Model):
    _inherit = 'account.move'

    department_id = fields.Many2one('hr.department', string=_("Department"))
    cost_item_id = fields.Many2one('bs.cost.item', string=_("Cost Item"))

    def action_fill_all_lines(self):
        """Заповнити department_id і cost_item_id у всіх рядках."""
        for record in self:
            for line in record.invoice_line_ids:
                line.department_id = record.department_id.id
                line.cost_item_id = record.cost_item_id.id

        # Показати повідомлення після заповнення всіх рядків
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('All lines have been filled successfully with department and cost item.'),
                'sticky': False,
                'type': 'success',
            }
        }

    def action_fill_empty_lines(self):
        """Заповнити department_id і cost_item_id тільки в рядках, де вони порожні."""
        for record in self:
            for line in record.invoice_line_ids:
                if not line.department_id:
                    line.department_id = record.department_id.id
                if not line.cost_item_id:
                    line.cost_item_id = record.cost_item_id.id

        # Показати повідомлення після заповнення порожніх рядків
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Empty lines have been filled successfully with department and cost item.'),
                'sticky': False,
                'type': 'success',
            }
        }