/**
* Dropbox Site List controller
* @namespace knownlyApp.controllers.dropboxsitelist
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.dropboxsitelist', [])
    .controller('DropboxSiteListController', DropboxSiteListController);

  DropboxSiteListController.$inject = ['DropboxSiteService', '$uibModal', '$mixpanel', '$log'];

  /**
  * @namespace DropboxSiteListController
  */
  function DropboxSiteListController(DropboxSiteService, $uibModal, $mixpanel, $log) {
    var viewModel = this;

    viewModel.dropboxSiteList = {};
    viewModel.$mixpanel = $mixpanel;
    
    activate();

    function activate() {
        return DropboxSiteService.getDropboxSiteList().then(function() {
          viewModel.dropboxSiteList = DropboxSiteService.dropboxSiteList;
        });
    }

    viewModel._deleteWebsite = function(websiteToDelete) {
      DropboxSiteService.deleteDropboxSite(websiteToDelete);
      $mixpanel.track("Delete Site button clicked");
    };

    // Website deletion confirmation modal

    viewModel.openDeleteDropboxSiteModal = function(websiteToDelete) {     
      var modalInstance = $uibModal.open({
        templateUrl: 'components/deletedropboxsitemodal/deletedropboxsitemodal.html',
        controller: 'DeleteDropboxSiteModalController',
        controllerAs: 'viewModel',
        resolve: {
          websiteToDelete: function () {
            return websiteToDelete;
          }
        }
      });

      modalInstance.result.then(function (websiteToDelete) {
        viewModel._deleteWebsite(websiteToDelete);
      });
    };
  }
})();
