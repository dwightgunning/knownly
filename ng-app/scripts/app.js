(function () {
  'use strict';

  var knownlyApp = angular.module('knownlyApp', [
    'ngRoute',
    'knownlyApp.services',
    'knownlyApp.controllers',
  ]);

  knownlyApp.config(['$locationProvider', '$routeProvider', '$httpProvider',
      function($locationProvider, $routeProvider, $httpProvider) {

    // Disable hash routing
    $locationProvider.hashPrefix('!');
    $locationProvider.html5Mode(true);
    
    // Use Django CSRF tokens
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';

    $routeProvider.when('/', {
      templateUrl: 'views/layouts/_domains.html',
      controller: 'DomainsController'
    });
    $routeProvider.otherwise({
      redirectTo: '/'
    });
  }]);

})();
