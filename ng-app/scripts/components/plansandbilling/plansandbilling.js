/**
* PlansAndBilling controller
* @namespace knownlyApp.controllers.account.plansandbilling
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account.plansandbilling', [])
    .controller('PlansAndBillingController', PlansAndBillingController);

  PlansAndBillingController.$inject = ['VouchersService', '$log'];

  /**
  * @namespace PlansAndBillingController
  */
  function PlansAndBillingController(VouchersService, $log) {
  	var viewModel = this;

    viewModel.voucherRedemptionForm = {};
    viewModel.voucherToRedeem = '';
    viewModel.vouchersRedeemed = VouchersService.vouchersRedeemed;

    activate();

    function activate() {
        return VouchersService.listRedeemedVouchers();
    }

    viewModel.setActiveSection = function(sectionName) {
      viewModel.activeSection = sectionName;
    };

    viewModel.submitVoucherRedemption = function() {
      viewModel.saving = true;

      if (!viewModel.voucherToRedeem.trim()) {
        return;
      }

      VouchersService.submitVoucherRedemption(viewModel.voucherToRedeem)
        .then(function success() {
          viewModel.voucherRedemptionForm.voucherToRedeem = '';
        })
        .catch(function(error) {
          viewModel.voucherRedemptionForm.voucherToRedeemField.$errors = error;
        })
        .finally(function () {
          viewModel.saving = false;
        });

      return true;
    };
  }

})();
