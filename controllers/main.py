from odoo import http, fields
from odoo.http import request
import werkzeug
import logging
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)
_logger = logging.getLogger(__name__)


class WebXPayController(http.Controller):
    def _split_name(self, full_name):
        if not full_name:
            return '', ''
        parts = full_name.split(' ', 1)
        return parts[0], parts[1] if len(parts) > 1 else ''

    def _split_address(self, street):
        if not street:
            return '', ''
        lines = street.split('\n', 1)
        return lines[0], lines[1] if len(lines) > 1 else ''

    @http.route(['/payment/webxpay/redirect'], type='http', auth='public', website=True)
    def webxpay_redirect(self, **post):
        try:
            order = request.website.sale_get_order()
            if not order:
                return werkzeug.utils.redirect('/shop')

            acquirer = request.env['payment.acquirer'].sudo().search([
                ('provider', '=', 'webxpay'),
                ('state', 'in', ['enabled', 'test'])
            ], limit=1)

            payment_data = f"{order.name}|{order.amount_total}"
            _logger.info("Payment data before encryption: %s", payment_data)

            public_key = acquirer.webxpay_public_key
            if not public_key.startswith('-----BEGIN PUBLIC KEY-----'):
                public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
            
            payment = self.encrypt_payment_data(payment_data, public_key)

            first_name, last_name = self._split_name(order.partner_id.name)
            address_line_one, address_line_two = self._split_address(order.partner_id.street)

            custom_fields = base64.b64encode(b'cus_1|cus_2|cus_3|cus_4').decode('utf-8')

            webxpay_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': order.partner_id.email or '',
                'contact_number': order.partner_id.phone or '',
                'address_line_one': address_line_one,
                'address_line_two': address_line_two,
                'city': order.partner_id.city or '',
                'state': order.partner_id.state_id.name or '',
                'postal_code': order.partner_id.zip or '',
                'country': order.partner_id.country_id.name or '',
                'process_currency': order.currency_id.name,
                'cms': 'Odoo',
                'custom_fields': custom_fields,
                'enc_method': 'JCs3J+6oSz4V0LgE0zi/Bg==',
                'secret_key': acquirer.webxpay_secret_key,
                'payment': payment,
            }

            _logger.info("Full WebXPay form data: %s", webxpay_data)

            return request.render('payment_webxpay.redirect_form', {
                'webxpay_url': acquirer.webxpay_api_url,
                'webxpay_data': webxpay_data,
            })

        except Exception as e:
            _logger.error("Error processing WebXPay payment: %s", str(e))
            return werkzeug.utils.redirect('/shop/payment')

    @http.route(['/payment/webxpay/callback'], type='http', auth='public', csrf=False)
    def webxpay_callback(self, **post):
        _logger.info("Received WebXPay callback with post data: %s", post)

        try:
            payment = base64.b64decode(post.get('payment', ''))
            signature = base64.b64decode(post.get('signature', ''))
            custom_fields = base64.b64decode(post.get('custom_fields', ''))

            _logger.info("Decoded payment data: %s", payment)
            _logger.info("Decoded custom fields: %s", custom_fields)

            response_data = payment.decode('utf-8').split('|')
            _logger.info("Response data: %s", response_data)

            if len(response_data) >= 4:
                order_id = response_data[0]
                status_code = response_data[3]

                order = request.env['sale.order'].sudo().search([
                    ('name', '=', order_id)
                ], limit=1)

                if not order:
                    _logger.error("Order not found: %s", order_id)
                    return werkzeug.utils.redirect('/shop/payment?error=order_not_found')

                if status_code == '0':
                    _logger.info("Payment successful for order %s", order_id)
                    order.write({
                        'state': 'sale',
                        'date_order': fields.Datetime.now()
                    })
                    return werkzeug.utils.redirect('/shop/confirmation')
                else:
                    error_message = response_data[4] if len(response_data) > 4 else 'Payment Failed'
                    _logger.error("Payment failed for order %s: %s", order_id, error_message)
                    return werkzeug.utils.redirect(f'/shop/payment?error={error_message}')

            return werkzeug.utils.redirect('/shop/payment?error=invalid_response')

        except Exception as e:
            _logger.error("Error processing WebXPay callback: %s", str(e))
            return werkzeug.utils.redirect('/shop/payment?error=processing_error')

    def encrypt_payment_data(self, payment_data, public_key):
        try:
            if not public_key.startswith('-----BEGIN PUBLIC KEY-----'):
                public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

            key = RSA.importKey(public_key.encode('utf-8'))
            cipher = PKCS1_v1_5.new(key)

            encrypted = cipher.encrypt(payment_data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            _logger.error("Encryption error: %s", str(e))
            raise
