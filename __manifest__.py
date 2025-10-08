{
    'name': 'WebXPay Payment API',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'summary': 'Payment Provider: WebXPay Implementation',
    'description': """WebXPay Payment Provider Integration""",
    'author': 'Chandika Rathnayake',
    'depends': [
	'base',
        'payment',
        'account',
        'website_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
	'data/payment_provider_data.xml',
        'views/payment_provider_views.xml',
        #'views/templates.xml',
	'views/payment_webxpay_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'webxpay_payment_api/static/src/js/payment.js',
            'webxpay_payment_api/static/src/css/style.css',
        ],
    },
    'application': True,
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'sequence': 1000,
#    'post_init_hook': '_create_missing_payment_provider',
}
