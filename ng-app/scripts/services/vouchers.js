/**
* Vouchers
* @namespace knownlyApp.services.vouchers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.vouchers', [])
    .factory('VouchersService', VouchersService);

  VouchersService.$inject = ['$http', '$q'];

  /**
    * @namespace VouchersService
    * @returns {Factory}
    */
  function VouchersService($http, $q) {
    /**
    * @name VouchersService
    * @desc The Factory to be returned
    */
    var _VouchersService = {
      'submitVoucherClaim': submitVoucherClaim,
      'listClaimedVouchers': listClaimedVouchers
    };

    return _VouchersService;

    function submitVoucherClaim() {
      console.log("Submitting voucher code");
    }

    function listClaimedVouchers() {
      console.log("Submitting voucher code");
    }

    // Service methods

    // function searchDomains(searchTerm) {
    //   var deferred = $q.defer();

    //   $http.post('/domains/search/?query=' + searchTerm)
    //     .then(function(data, status, headers, config) {
    //       deferred.resolve(data.data.results);
    //     }, function(data, status, headers, config) {
    //       return deferred.reject(undefined);
    //     });

    //   return deferred.promise;
    // }

    // function getDomainStatuses(domains) {
    //   var deferred = $q.defer();

    //   $http.post('/domains/status/?domain=' + domains.join('%2C'))
    //     .then(function(data, status, headers, config) {
    //       deferred.resolve(data.data.status);
    //     }, function(data, status, headers, config) {
    //       return deferred.reject(undefined);
    //     });

    //   return deferred.promise;
    // }
  }
})();
