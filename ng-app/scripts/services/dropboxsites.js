/**
* Dropbox Site service
* @namespace knownlyApp.services.dropboxsite
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.services.dropboxsite', [])
    .factory('DropboxSiteService', DropboxSiteService);

  DropboxSiteService.$inject = ['$http', '$q', '$log'];

  /**
    * @namespace AccountService
    * @returns {Factory}
    */
  function DropboxSiteService($http, $q, $log) {
    /**
    * @name DropboxSiteService
    * @desc The Factory to be returned
    */
    var service = {
      'dropboxSiteList': [],
      'getDropboxSiteList': getDropboxSiteList,
      'deleteDropboxSite': deleteDropboxSite,
      'createDropboxSite': createDropboxSite
    };

    return service;

    ////////////////////////

    function getDropboxSiteList() {
      return $http({
                    url: '/api/dropboxsite/', 
                    method: 'get',
                    headers: {'Content-Type': 'application/json'}
                  })
        .then(getDropboxSiteListComplete)
        .catch(getDropboxSiteListFailed);

      function getDropboxSiteListComplete(data, status, headers, config) {
        angular.copy(data.data, service.dropboxSiteList);
      }

      function getDropboxSiteListFailed(error) {
        $log.error('XHR Failed for getDropboxSiteList.');
        if ('error' in error.data) {
          return $q.reject(error.data.error);
        } else {
          return $q.reject('An unexpected error occurred.');
        }
      }
    }

    function createDropboxSite(domain) {
      var requestData = {
        'domain': domain,
      };

      return $http({
                    url: '/api/dropboxsite/', 
                    method: 'post',
                    headers: {'Content-Type': 'application/json'},
                    data: requestData
                  })
        .then(createDropboxSiteComplete)
        .catch(createDropboxSiteFailed);

      function createDropboxSiteComplete(data, status, headers, config) {
        service.dropboxSiteList.push(data.data);
      }

      function createDropboxSiteFailed(error) {
        $log.error('XHR Failed for createDropboxSite.');
        if (error.data) {
          return $q.reject(error.data);
        } else {
          return $q.reject('An unexpected error occurred.');
        }
      }      
    }

    function deleteDropboxSite(domain) {
      return $http({
                    url: '/api/dropboxsite/' + domain + '/', 
                    method: 'delete'
                  })
        .then(deleteDropboxSiteComplete)
        .catch(deleteDropboxSiteFailed);

      function deleteDropboxSiteComplete(data, status, headers, config) {
        // Removing the deleted website from the service's list
        // involves creating a new list (based on filter) and deep
        // copying it back into place
        var updatedList = service.dropboxSiteList.filter(function(obj) {
          return domain != obj.domain;
        });
        angular.copy(updatedList, service.dropboxSiteList);
      }

      function deleteDropboxSiteFailed(error) {
        $log.error('XHR Failed for deleteDropboxSite.');
        if ('error' in error.data) {
          return $q.reject(error.data.error);
        } else {
          return $q.reject('An unexpected error occurred.');
        }
      }
    }
  }
})();
