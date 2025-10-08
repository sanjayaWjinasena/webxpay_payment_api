from odoo import api, models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'webxpay':
            return res

        return {
            'api_url': 'https://stagingxpay.info/index.php?route=checkout/billing' if self.provider_id.state == 'test' else 'https://stagingxpay.info/index.php?route=checkout/billing',
            'merchant_id': self.provider_id.webxpay_api_username,
            'transaction_id': self.reference,
            'amount': processing_values['amount'],
            'currency': self.currency_id.name,
        }
