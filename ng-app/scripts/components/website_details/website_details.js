/**
* Website Details controller
* @namespace knownlyApp.controllers.website_details
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.website_details', [])
    .controller('WebsiteDetailsController', WebsiteDetailsController);

  WebsiteDetailsController.$inject = ['$stateParams'];

  /**
  * @namespace WebsiteDetailsController
  */
  function WebsiteDetailsController($stateParams) {
  	var viewModel = this;

    viewModel.domain = $stateParams.domain;
  }

})();
