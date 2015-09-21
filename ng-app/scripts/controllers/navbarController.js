/**
* NavbarController
* @namespace knownlyApp.controllers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers')
    .controller('NavbarController', NavbarController);

  NavbarController.$inject = ['$scope', 'AuthenticationService'];

  /**
  * @namespace NavbarController
  */
  function NavbarController($scope, AuthenticationService) {
    var viewModel = this;

    viewModel.logout = logout;

    AuthenticationService.getAuthenticatedUserAccount().then(
      function(userAccount) {
        viewModel.userAccount = userAccount;
      }, function() {
        // Handle authentication error
        console.log("No authenticated user");
        window.location = '/';
      });

    /**
    * @name logout
    * @desc Log the user out
    * @memberOf knownlyApp.controllers.NavbarController
    */
    function logout() {
      AuthenticationService.logout();
    }
  }
})();
