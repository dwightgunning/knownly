/**
* Profile controller
* @namespace knownlyApp.controllers.account.profile
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.account.profile', [])
    .controller('ProfileController', ProfileController);

  ProfileController.$inject = ['$timeout', 'AccountService', '$log'];

  /**
  * @namespace ProfileController
  */
  function ProfileController($timeout, AccountService, $log) {
  	var viewModel = this;

    viewModel.profileForm = {};
    viewModel.profile = {};
    viewModel.showSuccess = false;

    activate();

    function activate() {
        return AccountService.getProfile().then(function() {
          viewModel.profile = angular.copy(AccountService.profile);
        });
    }

    viewModel.submitProfileForm = function() {
      if (viewModel.profileForm.$invalid) {
        return;
      }

      AccountService.updateProfile(viewModel.profile)
        .then(function success() {
          viewModel.profile = angular.copy(AccountService.profile);
          viewModel.profileForm.$setPristine();
          viewModel.profileForm.$setUntouched();

          viewModel.showSuccess = true;
          $timeout(function() {
            viewModel.showSuccess = false;
          }, 3000);
        })
        .catch(function(formerrors) {
          _.each(formerrors, function(fielderrors, field) {
              _.each(fielderrors, function(fielderror) {
                viewModel.profileForm[field].$dirty = true;
                viewModel.profileForm[field].$setValidity(fielderror, false);
              });
            });
        });

      return true;
    };

    viewModel.resetProfileForm = function() {
      viewModel.profileForm.$setPristine();
      viewModel.profileForm.$setUntouched();

      viewModel.profile = angular.copy(AccountService.profile);
    };

  }

})();
