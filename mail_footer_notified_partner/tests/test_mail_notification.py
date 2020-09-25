# © 2016 ACSONE SA/NV <https://acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import odoo.tests.common as common


class TestMailNotification(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.sender = self.env['res.partner'].create({
            'name': 'Test sender',
            'email': 'sender@example.com',
        })
        self.recipient = self.env['res.partner'].create({
            'name': 'Test recipient',
            'email': 'recipient@example.com',
        })
        self.other_recipient = self.env['res.partner'].create({
            'name': 'Other test recipient',
            'email': 'otherrecipient@example.com',
        })
        self.recipients = self.recipient + self.other_recipient
        self.msg_vals = {
            'subject': 'Message test',
            'author_id': self.sender.id,
            'email_from': self.sender.email,
            'message_type': 'comment',
            'model': 'res.partner',
            'res_id': self.recipient.id,
            'body': '<p>This is a test message</p>',
        }

        self.record = self.recipient
        self.force_send = True
        self.send_after_commit = True
        self.model_description = False
        self.mail_auto_delete = True

    def notify_record(self, msg_vals, message):
        rdata = message._notify_compute_recipients(self.record, msg_vals)
        return self.recipients._notify(
            message,
            rdata["partners"],
            self.record,
            self.force_send,
            self.send_after_commit,
            self.model_description,
            self.mail_auto_delete,
        )

    def test_get_signature_footer(self):
        """If more than one recipient are notified, each should be mentioned
           in the 'also notified' at the end of the message body.
        """
        msg_vals = self.msg_vals.copy()
        msg_vals['partner_ids'] = [(4, r.id) for r in self.recipients]
        message = self.env['mail.message'].create(msg_vals)
        rep = self.notify_record(msg_vals, message)

        self.assertTrue(rep, "message not send")
        self.assertTrue(
            self.recipient.name in message.body,
            "Partner name is not in the body of the mail",
        )
        self.assertTrue(
            self.other_recipient.name in message.body,
            "Other partner name is not in the body of the mail",
        )

    def test_get_signature_no_footer(self):
        """If there is only one recipient, no need to add the also notified."""
        msg_vals = self.msg_vals.copy()
        msg_vals['partner_ids'] = [(4, self.recipient.id)]
        message = self.env['mail.message'].create(msg_vals)
        rep = self.notify_record(msg_vals, message)

        self.assertTrue(rep, "message not send")
        self.assertFalse(
            self.recipient.name in message.body,
            "Partner name should not be in the body of the mail",
        )
