/**
* Vouchers controller
* @namespace knownlyApp.controllers.account.vouchers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account.vouchers', [])
    .controller('VouchersController', VouchersController);

  VouchersController.$inject = ['VouchersService', '$log'];

  /**
  * @namespace VouchersController
  */
  function VouchersController(VouchersService, $log) {
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
