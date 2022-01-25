# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class MailTemplateReport(models.Model):
    """
    Model used to define dynamic report generation on email template
    """

    _name = "mail.template.report"
    _description = "Mail template report"

    mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Mail template",
        required=True,
        ondelete="cascade",
    )
    model = fields.Char(compute="_compute_model", store=True)
    path = fields.Char()
    report_template_id = fields.Many2one(
        comodel_name="ir.actions.report",
        string="Report",
        required=True,
        ondelete="cascade",
    )
    report_name = fields.Char(translate=True)

    @api.depends("path", "mail_template_id.model")
    def _compute_model(self):
        for report in self:
            report.model = report.mail_template_id.model
            if report.path:
                report.model = self._get_model_by_recursive_path(
                    self.env[report.mail_template_id.model], report.path
                )

    @api.model
    def _get_model_by_recursive_path(self, model, path):
        split_path = path.split(".")
        field_name = split_path.pop(0)
        field = model._fields.get(field_name)
        if not field:
            raise ValidationError(
                _("Path is invalid.")
            )
        if field.type != "many2one":
            raise ValidationError(
                _("Path can only consist of many2one's.")
            )
        if not split_path:
            return field.comodel_name
        return self._get_model_by_recursive_path(
            self.env[field.comodel_name],
            ".".join(split_path)
        )

    def get_active_res_id(self, record):
        self.ensure_one()
        if not self.path:
            return record
        return safe_eval("record.%s.id" % self.path, {
            "record": record
        })
