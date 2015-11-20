/**
* Account service
* @namespace knownlyApp.services.account
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.account', [])
    .factory('AccountService', AccountService);

  AccountService.$inject = ['$http', '$q', '$log'];

  /**
    * @namespace AccountService
    * @returns {Factory}
    */
  function AccountService($http, $q, $log) {
    /**
    * @name AccountService
    * @desc The Factory to be returned
    */
    var service = {
      'profile': {},
      'getProfile': getProfile,
      'updateProfile': updateProfile
    };

    return service;

    ////////////////////////

    function getProfile() {
      return $http({
                    url: '/api/account/profile/', 
                    method: 'get',
                    headers: {'Content-Type': 'application/json'}
                  })
        .then(getProfileComplete)
        .catch(getProfileFailed);

      function getProfileComplete(data, status, headers, config) {
        angular.copy(data.data, service.profile);
      }

      function getProfileFailed(error) {
        $log.error('XHR Failed for getProfile.');
        if ('error' in error.data) {
          return $q.reject(error.data.error);
        } else {
          return $q.reject('An unexpected error occurred.');
        }
      }
    }

    function updateProfile(profile) {

      return $http({
                    url: '/api/account/profile/',
                    method: 'put',
                    headers: {'Content-Type': 'application/json'},
                    data: profile
                  })
        .then(updateProfileComplete)
        .catch(updateProfileFailed);

      function updateProfileComplete(data, status, headers, config) {
        angular.copy(data.data, service.profile);
      }

      function updateProfileFailed(error) {
        $log.error('XHR Failed for updateProfile.');
        if (error.data) {
          return $q.reject(error.data);
        } else {
          return $q.reject('An unexpected error occurred.');
        }
      }
    }
  }
})();
