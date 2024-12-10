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

    def action_distribute_evenly(self):
        for cost_item in self:
            departments = cost_item.department_ids
            num_departments = len(departments)
            if num_departments > 0:
                percentage_per_department = 100 / num_departments
                for department in departments:
                    department.write({'percentage': percentage_per_department})

    def action_add_all_departments(self):
        for cost_item in self:
            # Отримуємо всі відділи, що можуть бути використані для розподілу
            departments = self.env['hr.department'].search([('allocate_expenses', '=', True)], order='name')
            for department in departments:
                # Додаємо відділ, якщо його ще немає в списку
                if department.id not in cost_item.department_ids.mapped('department_id.id'):
                    self.env['bs.cost.item.department'].create({
                        'cost_item_id': cost_item.id,
                        'department_id': department.id,
                        'percentage': 0.0,  # Не заповнюємо відсоток
                    })

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