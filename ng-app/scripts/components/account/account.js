/**
* Account controller
* @namespace knownlyApp.controllers.account
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account', [])
    .controller('AccountController', AccountController);

  AccountController.$inject = ['$log'];

  /**
  * @namespace AccountController
  */
  function AccountController($log) {
    var viewModel = this;
  }
})();
