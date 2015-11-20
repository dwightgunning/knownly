/**
* Navbar controller
* @namespace knownlyApp.controllers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.navbar', [])
    .controller('NavbarController', NavbarController);

  NavbarController.$inject = ['AuthenticationService'];

  /**
  * @namespace NavbarController
  */
  function NavbarController(AuthenticationService) {
    var viewModel = this;

    viewModel.logout = logout;

    AuthenticationService.getAuthenticatedUserAccount().then(
      function(userAccount) {
        viewModel.userAccount = userAccount;
      }, function() {
        // Handle authentication error
        window.location = '/';
      });

    function logout() {
      AuthenticationService.logout();
    }
  }
})();
