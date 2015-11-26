/**
* Create Dropbox Site Form controller
* @namespace knownlyApp.controllers.createdropboxsiteform
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.createdropboxsiteform', [])
    .controller('CreateDropboxSiteFormController', CreateDropboxSiteFormController);

  CreateDropboxSiteFormController.$inject = ['$timeout', 'DropboxSiteService', '$mixpanel'];

  /**
  * @namespace CreateDropboxSiteFormController
  */
  function CreateDropboxSiteFormController($timeout, DropboxSiteService, $mixpanel) {
    var viewModel = this;

    viewModel.createDropboxSiteForm = {};
    viewModel.dropboxSite = {};
    viewModel.showSuccess = false;

    viewModel.clearFieldServerErrors = function(field) {
      if (viewModel.createDropboxSiteForm[field].serverErrors) {
        viewModel.createDropboxSiteForm[field].$setValidity('server-field', true);
        viewModel.createDropboxSiteForm[field].serverErrors.length = 0;
      }
      if (viewModel.createDropboxSiteForm.serverErrors) {
        viewModel.createDropboxSiteForm.$setValidity('server', true);
        viewModel.createDropboxSiteForm.serverErrors.length = 0;
      }
    };

    viewModel.submitCreateDropboxSiteForm = function() {
      if (viewModel.createDropboxSiteForm.$invalid) {
        return;
      }

      DropboxSiteService.createDropboxSite(viewModel.dropboxSite.domain)
        .then(function success() {
          viewModel.dropboxSite = {};
          viewModel.createDropboxSiteForm.$setPristine();
          viewModel.createDropboxSiteForm.$setUntouched();

          viewModel.showSuccess = true;
          $timeout(function() {
            viewModel.showSuccess = false;
          }, 3000);
          $mixpanel.track('Create Site button clicked');
        })
        .catch(function(formerrors) {
          _.each(formerrors, function(errors, field) {
            if (field in viewModel.createDropboxSiteForm) {
              viewModel.createDropboxSiteForm[field].serverErrors = errors;
              viewModel.createDropboxSiteForm[field].$dirty = true;
              viewModel.createDropboxSiteForm[field].$setValidity('server-field', false);
            } else {
              viewModel.createDropboxSiteForm.serverErrors = errors;
              viewModel.createDropboxSiteForm.$dirty = true;
              viewModel.createDropboxSiteForm.$setValidity('server', false);
            }
            });
        });

      return true;
    };

  }
})();
