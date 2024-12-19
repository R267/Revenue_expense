from odoo import models, fields, api, _

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

        # Показати повідомлення після заповнення
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

        # Показати повідомлення після заповнення
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

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    department_id = fields.Many2one(
        'hr.department',
        string=_("Department"),
        help="Department linked to this line.",
        readonly=False,
        tracking=True,
        compute='_compute_visible_fields',
        store=True,
    )
    cost_item_id = fields.Many2one(
        'bs.cost.item',
        string=_("Cost Item"),
        help="Cost item linked to this line.",
        readonly=False,
        tracking=True,
        compute='_compute_visible_fields',
        store=True,
    )

    @api.depends('move_id.move_type')
    def _compute_visible_fields(self):
        """ Відображати поля тільки для рахунків постачальника """
        for line in self:
            if line.move_id.move_type == 'in_invoice':
                line.department_id = line.department_id
                line.cost_item_id = line.cost_item_id
            else:
                line.department_id = False
                line.cost_item_id = False

    @api.onchange('product_id')
    def _onchange_product_id_fill_department_and_cost_item(self):
        """Automatically fill Department and Cost Item when a product is selected."""
        for line in self:
            if line.move_id.move_type == 'in_invoice' and line.product_id:
                # Set the department and cost item if they are defined on the product
                line.department_id = line.product_id.department_id.id
                line.cost_item_id = line.product_id.cost_item_id.id
