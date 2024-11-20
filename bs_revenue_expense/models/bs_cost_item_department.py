from odoo import models, fields, _

class BSCostItemDepartment(models.Model):
    _name = 'bs.cost.item.department'
    _description = 'Cost Item Department Allocation'

    cost_item_id = fields.Many2one(
        'bs.cost.item',
        string=_("Cost Item"),
        ondelete='cascade',
        required=True
    )
    department_id = fields.Many2one(
        'hr.department',
        string=_("Department"),
        required=True,
        domain="[('allocate_expenses', '=', True)]",
    )
    percentage = fields.Float(
        string=_("Percentage"),
        required=True
    )
