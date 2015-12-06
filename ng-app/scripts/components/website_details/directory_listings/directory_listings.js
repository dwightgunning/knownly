/**
* Website Directory Listings controller
* @namespace knownlyApp.controllers.website_details.directory_listings
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.website_details.directory_listings', [])
    .controller('WebsiteDirectoryListingsController', WebsiteDirectoryListingsController);

  WebsiteDirectoryListingsController.$inject = ['$stateParams'];

  /**
  * @namespace WebsiteDirectoryListingsController
  */
  function WebsiteDirectoryListingsController($stateParams) {
  	var viewModel = this;

    viewModel.domain = $stateParams.domain;

    console.log("The controller lives");
  }

})();
