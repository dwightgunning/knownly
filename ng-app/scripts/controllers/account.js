/**
* Account controller
* @namespace knownlyApp.controllers.account
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account', [])
    .controller('AccountController', AccountController);

  AccountController.$inject = ['_', '$scope', 'VouchersService', '$log'];

  /**
  * @namespace AccountController
  */
  function AccountController(_, $scope, VouchersService, $log) {
    var viewModel = this;
    var defaultSection = 'profile';

    viewModel.activeSection = defaultSection;

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
