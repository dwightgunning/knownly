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
    $scope.flatSearchResults = []; // Standard allmighty-autocomplete directive expects a flat array
    $scope.domainSearchResults = {}; // Custom directive should work with an assoc. array that combines the domain name + status

    $scope.searchDomains = function(searchTerm){
      var results = DomainsService.searchDomains(searchTerm);
      results.then(function(searchResults){
        $scope.domainSearchResults = searchResults;
        $scope.flatSearchResults = _.pluck(searchResults, 'domain');

        var domains_without_status = _.filter(searchResults, function(domain) {
          return !('status' in domain);
        });
        domains_without_status = _.pluck(domains_without_status, 'domain');

        var domainStatusResults = DomainsService.getDomainStatuses(domains_without_status);
        domainStatusResults.then(function(domainStatuses){
          _.each(domainStatuses, function(domainStatus) {
            var domain = _.findWhere($scope.domainSearchResults, {domain: domainStatus.domain});
            if (domain !== undefined) {
             domain.status = domainStatus;
            }
          });
        });
      });
    };
  }
})();
