/*odoo.define('webxpay_payment.payment', function (require) {
    'use strict';

    var core = require('web.core');
    var publicWidget = require('web.public.widget');

    publicWidget.registry.WebXPayForm = publicWidget.Widget.extend({
        selector: '.webxpay-form',
        events: {
            'click #webxpay_checkout_button': '_onClickPay',
        },

        _onClickPay: function (ev) {
            ev.preventDefault();
	    console.log('WebXPay button clicked - redirecting to payment gateway');
            ev.stopPropagation();
            this.el.submit();
        },
    });

    return publicWidget.registry.WebXPayForm;
});
*/
/*
odoo.define('webxpay_payment.payment', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.WebXPayButton = publicWidget.Widget.extend({
        selector: '.webxpay-button-container',
        events: {
            'click #webxpay_redirect_button': '_onClickWebXPayButton',
        },

        _onClickWebXPayButton: function (ev) {
            ev.preventDefault();
	    console.log('WebXPay button clicked - redirecting to payment gateway');
            window.location.href = '/payment/webxpay/redirect';
        },
    });
});
*/

odoo.define('webxpay_payment.payment', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.WebXPayButton = publicWidget.Widget.extend({
        selector: '.webxpay-button-container',
        events: {
            'click #webxpay_redirect_button': '_onClickWebXPayButton',
        },

        /**
         * @override
         */
        start: function () {
            console.log('WebXPay widget initialized'); // Debug initialization
            return this._super.apply(this, arguments);
        },

        /**
         * @private
         * @param {Event} ev
         */
        _onClickWebXPayButton: function (ev) {
            console.log('WebXPay button clicked'); // Debug click event
            ev.preventDefault();
            ev.stopPropagation();
            console.log('Redirecting to:', 'webxpay'); // Debug redirect URL
            window.location.href = '/payment/webxpay/redirect';
        },
    });

    publicWidget.registry.WebXPayButton.include({
        /**
         * @override
         */
        destroy: function () {
            console.log('WebXPay widget destroyed'); // Debug destruction
            this._super.apply(this, arguments);
        },
    });
});
