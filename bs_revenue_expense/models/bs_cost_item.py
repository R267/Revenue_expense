from odoo import models, fields, api, _

class BSCostItem(models.Model):
    _name = 'bs.cost.item'
    _description = 'Cost Item'

    name = fields.Char(required=True, string=_("Name"))
    description = fields.Text(string=_("Description"))
    allocate_to_departments = fields.Boolean(
        string=_("Allocate to Departments"),
        help="Enable allocation to departments."
    )
    department_ids = fields.One2many(
        'bs.cost.item.department',
        'cost_item_id',
        string=_("Departments")
    )

    @api.constrains('department_ids')
    def _check_percentage_total(self):
        for record in self:
            if record.allocate_to_departments:
                total = sum(record.department_ids.mapped('percentage'))
                if total != 100:
                    raise models.ValidationError("Total percentage must equal 100%.")

class HRDepartment(models.Model):
    _inherit = 'hr.department'

    allocate_expenses = fields.Boolean(
        string=_("Allocate Expenses"),
        help="Enable expense allocation for this department."
    )
    allocate_revenues = fields.Boolean(
        string=_("Allocate Revenues"),
        help="Enable revenue allocation for this department."
    )