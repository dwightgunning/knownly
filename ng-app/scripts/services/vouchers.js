/**
* Vouchers
* @namespace knownlyApp.services.vouchers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.vouchers', [])
    .factory('VouchersService', VouchersService);

  VouchersService.$inject = ['$http', '$q', '$log'];

  /**
    * @namespace VouchersService
    * @returns {Factory}
    */
  function VouchersService($http, $q, $log) {
    /**
    * @name VouchersService
    * @desc The Factory to be returned
    */
    var service = {
      'vouchersRedeemed': [],
      'submitVoucherRedemption': submitVoucherRedemption,
      'listRedeemedVouchers': listRedeemedVouchers
    };

    return service;

    ////////////////////////

    function submitVoucherRedemption(voucherCode) {
      var requestData = {'voucher_code': voucherCode};

      return $http({
                    url: '/api/vouchers/', 
                    method: 'post',
                    headers: {'Content-Type': 'application/json'},
                    data: requestData
                  })
        .then(submitVoucherRedemptionComplete)
        .catch(submitVoucherRedemptionFailed);

      function submitVoucherRedemptionComplete(data, status, headers, config) {
        service.vouchersRedeemed.push(data.data);
      }

      function submitVoucherRedemptionFailed(error) {
        $log.error('XHR Failed for submitVoucherRedemptionFailed.');
        if ('error' in error.data) {
          return $q.reject(error.data.error);
        } else {
          return $q.reject('An unexpected error occurred.');
        }
      }
    }

    function listRedeemedVouchers() {
      return $http({
                    url: '/api/vouchers/', 
                    method: 'get',
                    headers: {'Content-Type': 'application/json'}
                  })
        .then(listRedeemedVouchersComplete)
        .catch(listRedeemedVouchersFailed);

      function listRedeemedVouchersComplete(data, status, headers, config) {
        angular.copy(data.data, service.vouchersRedeemed);
      }

      function listRedeemedVouchersFailed(error) {
        $log.error('XHR Failed for listRedeemedVouchers.');
      }
    }
  }
})();
