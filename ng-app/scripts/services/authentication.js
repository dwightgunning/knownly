/**
* Authentication service
* @namespace knownlyApp.services
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.authentication', [])
    .factory('AuthenticationService', AuthenticationService);

  AuthenticationService.$inject = ['$http', '$q'];

  /**
    * @namespace AuthenticationService
    * @returns {Factory}
    */
  function AuthenticationService($http, $q) {
    /**
    * @name AuthenticationService
    * @desc The Factory to be returned
    */
    var service = {
      'userProfile': {},
      'logout': logout,
      'getUserProfile': getUserProfile,
    };

    return service;

    ////////////////////////

    function logout() {
      return $http
        .post('/api/logout/')
        .then(logoutSuccess, logoutError);

      function logoutSuccess(response, status, headers, config) {
        service.userProfile = undefined;
        window.location = '/';
      }

      function logoutError(response, status, headers, config) {
        console.error('Logout failed.');
      }
    }

    function getUserProfile() {
      var deferred = $q.defer();

      return $http.
        get('/api/account/profile/')
        .then(getUserProfileSuccess, getUserProfileError);

      function getUserProfileSuccess(response, status, headers, config) {
        angular.copy(response.data, service.userProfile);
      }

      function getUserProfileError(response, status, headers, config) {
        service.logout();
      }
    }
  }
})();
