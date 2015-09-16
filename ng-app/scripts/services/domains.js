var services = angular.module('knownlyApp.services', []);

services.factory('DomainsService', ['$http', function($http) {

  var Domains = function() {
    angular.extend(this);
  };

  return Domains;
}]);
