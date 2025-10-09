import base64
import logging
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from werkzeug import urls

_logger = logging.getLogger(__name__)

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    provider = fields.Selection(
        selection_add=[('webxpay', 'WebXPay')],
        ondelete={'webxpay': 'set default'} # changed to 'set null' from 'cascade'
    )
    webxpay_api_url = fields.Char(
        string='API URL',
        required_if_provider='webxpay',
        default='https://stagingxpay.info/index.php?route=checkout/billing'
    )
    webxpay_callback_url = fields.Char(
        string='Callback URL',
        required_if_provider='webxpay',
	default='/payment/webxpay/callback'
    )
    webxpay_api_username = fields.Char(
        string='API Username',
        help='The API username provided by WebXPay',
        required_if_provider='webxpay',
    )
    webxpay_api_password = fields.Char(
        string='API Password',
        help='The API password provided by WebXPay',
        required_if_provider='webxpay',
    )
    webxpay_secret_key = fields.Char(
        string='Secret Key',
        help='The secret key provided by WebXPay',
        required_if_provider='webxpay',
    )
    webxpay_public_key = fields.Text(
        string='Public Key',
        help='The public key provided by WebXPay',
        required_if_provider='webxpay',
    )

    def _get_default_provider(self):
        return 'webxpay'

    def _get_webxpay_url(self, tx):
        """Generate the WebXPay payment URL."""
        base_url = 'https://stagingxpay.info/index.php?route=checkout/billing'

        payment_data = f"{tx.reference}|{tx.amount}"
        encrypted_payment = self._encrypt_payment_data(payment_data)

        params = {
            'first_name': tx.partner_id.name,
            'last_name': tx.partner_id.name,
            'email': tx.partner_id.email,
            'contact_number': tx.partner_id.phone or '',
            'address_line_one': tx.partner_id.street or '',
            'city': tx.partner_id.city or '',
            'country': tx.partner_id.country_id.name or '',
            'postal_code': tx.partner_id.zip or '',
            'cms': 'Odoo',
            'process_currency': tx.currency_id.name,
            'payment': encrypted_payment,
            'secret_key': self.webxpay_secret_key,
        }

        url = f"{base_url}?{werkzeug.urls.url_encode(params)}"
        _logger.info("Generated WebXPay URL: %s", url)
        return url

    @api.model
    def _get_compatible_providers(self, *args, currency_id=None, **kwargs):
        """ Override of payment to filter out WebXPay providers for unsupported currencies. """
        providers = super()._get_compatible_providers(*args, currency_id=currency_id, **kwargs)

        currency = self.env['res.currency'].browse(currency_id).exists()
        if currency and currency.name not in ['LKR', 'USD']:
            providers = providers.filtered(lambda p: p.code != 'webxpay')
        return providers
