/**
* Billing controller
* @namespace knownlyApp.controllers.account.billing
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account.billing', [])
    .controller('BillingController', BillingController);

  BillingController.$inject = ['$log'];

  /**
  * @namespace BillingController
  */
  function BillingController($log) {
  	var viewModel = this;
  }

})();
