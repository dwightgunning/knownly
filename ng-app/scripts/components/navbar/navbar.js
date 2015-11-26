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

    viewModel.userProfile = {};

    activate();

    function activate() {
        return AuthenticationService.getUserProfile().then(function() {
          viewModel.userProfile = AuthenticationService.userProfile;
        });
    }

    viewModel.logout = function() {
      AuthenticationService.logout();
    };
  }
})();
