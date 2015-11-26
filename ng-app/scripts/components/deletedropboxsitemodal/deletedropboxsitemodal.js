/**
* Delete Dropbox Site Modal controller
* @namespace knownlyApp.controllers.deletedropboxsitemodal
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.deletedropboxsitemodal', [])
    .controller('DeleteDropboxSiteModalController', DeleteDropboxSiteModalController);

  DeleteDropboxSiteModalController.$inject = ['$scope', '$uibModalInstance', 'websiteToDelete'];

  /**
  * @namespace DeleteDropboxSiteModalController
  */
  function DeleteDropboxSiteModalController($scope, $uibModalInstance, websiteToDelete) {
    var viewModel = this;
    viewModel.websiteToDelete = websiteToDelete;

    viewModel.ok = function () {
      $uibModalInstance.close(viewModel.websiteToDelete);
    };

    viewModel.cancel = function () {
      $uibModalInstance.dismiss('cancel');
    };

  }
})();
