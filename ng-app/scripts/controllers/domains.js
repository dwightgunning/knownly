/**
* Domains controller
* @namespace knownlyApp.controllers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.domains', [])
    .controller('DomainsController', DomainsController);

  DomainsController.$inject = ['_', '$scope', 'DomainsService'];

  /**
  * @namespace DomainsController
  */
  function DomainsController(_, $scope, DomainsService) {

    var viewModel = this;

    $scope.searchTerm = '';
    $scope.searchResults = [];

    $scope.searchDomains = function(searchTerm){
      var results = DomainsService.searchDomains(searchTerm);
      results.then(function(searchResults){
        $scope.searchResults = _.pluck(searchResults, 'domain');
      });
    };

  }
})();
