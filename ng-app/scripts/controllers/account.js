/**
* Account controller
* @namespace knownlyApp.controllers.account
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account', [])
    .controller('AccountController', AccountController);

  AccountController.$inject = ['_', '$scope', 'VouchersService'];

  /**
  * @namespace AccountController
  */
  function AccountController(_, $scope, VouchersService) {
    var viewModel = this;
    // var defaultSection = 'profile';
    var defaultSection = 'plansAndBilling';

    viewModel.activeSection = this.defaultSection;

    viewModel.setActiveSection = function(sectionName) {
      viewModel.activeSection = sectionName;
    };

    viewModel.submitVoucherClaim = function() {
      console.log("Controller method");
      VouchersService.submitVoucherClaim();
    };

    this.accountSections = {
      'plans-and-billing': {
          'controller': 'AccountPlansAndBillingController',
          'template': 'views/layouts/account/_plans_and_billing.html'
      },
      'profile': {
        'controller': 'AccountProfile',
        'template': 'views/layouts/account/_profile.html'
      }
    };
  }
})();
