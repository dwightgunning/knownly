/**
* Domains
* @namespace knownlyApp.services
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.domains', [])
    .factory('DomainsService', DomainsService);

  DomainsService.$inject = ['$http', '$q'];

  /**
    * @namespace DomainsService
    * @returns {Factory}
    */
  function DomainsService($http, $q) {
    /**
    * @name DomainsService
    * @desc The Factory to be returned
    */
    var _DomainsService = {
      searchDomains: searchDomains,
      getDomainStatuses: getDomainStatuses

    };

    return _DomainsService;

    // Service methods

    function searchDomains(searchTerm) {
      var deferred = $q.defer();

      $http.post('/domains/search/?query=' + searchTerm)
        .then(function(data, status, headers, config) {
          deferred.resolve(data.data.results);
        }, function(data, status, headers, config) {
          return deferred.reject(undefined);
        });

      return deferred.promise;
    }

    function getDomainStatuses(domains) {
      var deferred = $q.defer();

      $http.post('/domains/status/?domain=' + domains.join('%2C'))
        .then(function(data, status, headers, config) {
          deferred.resolve(data.data.status);
        }, function(data, status, headers, config) {
          return deferred.reject(undefined);
        });

      return deferred.promise;
    }
  }
})();
