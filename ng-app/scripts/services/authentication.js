/**
* Authentication
* @namespace knownlyApp.services
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.authentication', ['ngCookies'])
    .factory('AuthenticationService', AuthenticationService);

  AuthenticationService.$inject = ['$http', '$cookies', '$q'];

  /**
    * @namespace AuthenticationService
    * @returns {Factory}
    */
  function AuthenticationService($http, $cookies, $q) {
    /**
    * @name AuthenticationService
    * @desc The Factory to be returned
    */
    var _AuthenticationService = {
      logout: logout,
      'getAuthenticatedUserProfile': getAuthenticatedUserProfile,
      'setAuthenticatedUserProfile': setAuthenticatedUserProfile,
      unauthenticate: unauthenticate
    };

    return _AuthenticationService;

    // Service methods

    /**
     * @name logout
     * @desc Try to log the user out
     * @returns {Promise}
     * @memberOf knownlyApp.services.AuthenticationService
     */
    function logout() {
      return $http
        .post('/api/logout/')
        .then(completeLogout, logoutError);

        /**
         * @name logoutSuccess
         * @desc Unauthenticate and redirect to index with page reload
         */
        function completeLogout(data, status, headers, config) {
          _AuthenticationService.unauthenticate();
          window.location = '/';
        }

        /**
         * @name logoutError
         * @desc Log error. 
         */
        function logoutError(data, status, headers, config) {
          console.error('Logout failed.');
          completeLogout();
        }
    }

    /**
     * @name getAuthenticatedUserProfile
     * @desc Return the currently authenticated User
     * @returns {object|undefined} User if authenticated, else `undefined`
     * @memberOf knownlyApp.services.AuthenticationService
     */
    function getAuthenticatedUserProfile() {
      if (!$cookies.authenticatedUserProfile) {
        console.log("no available user account, fetching from server.");
        var deferred = $q.defer();

        $http.get('/api/account/profile/')
          .then(function(data, status, headers, config) {
            _AuthenticationService.setAuthenticatedUserProfile(data.data);
            deferred.resolve(JSON.parse($cookies.authenticatedUserProfile));
          }, function(data, status, headers, config) {
            AuthenticationService.unauthenticate();
            deferred.reject(undefined);
          });

          return deferred.promise;
      }

      return JSON.parse($cookies.authenticatedUserProfile);
    }

    /**
     * @name setAuthenticatedUserProfile
     * @desc Stringify the User object and store it in a cookie
     * @param {Object} user The User object to be stored
     * @returns {undefined}
     * @memberOf knownlyApp.services.AuthenticationService
     */
    function setAuthenticatedUserProfile(userProfile) {
      $cookies.authenticatedUserProfile = JSON.stringify(userProfile);
    }

    /**
     * @name unauthenticate
     * @desc Delete the cookie where the user object is stored
     * @returns {undefined}
     * @memberOf knownlyApp.services.AuthenticationService
     */
    function unauthenticate() {
      delete $cookies.authenticatedUserProfile;
    }

  }
})();
