(function () {
  'use strict';

  var knownlyApp = angular.module('knownlyApp', [
    'ngRoute',
    'autocomplete',
    'ngCookies',
    'knownlyApp.services.authentication',
    'knownlyApp.services.domains',
    'knownlyApp.services.vouchers',
    'knownlyApp.controllers.account',
    'knownlyApp.controllers.account.profile',
    'knownlyApp.controllers.account.plansAndBilling',
    'knownlyApp.controllers.domains',
    'knownlyApp.controllers.navbar'
  ]);

  knownlyApp.constant('_', window._);

  knownlyApp.config(['$locationProvider', '$routeProvider', '$httpProvider',
    function($locationProvider, $routeProvider, $httpProvider) {

    // Disable hash routing
    $locationProvider.hashPrefix('!');
    $locationProvider.html5Mode(true);
    
    // Use Django CSRF tokens
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';

    $routeProvider.when('/', {
      templateUrl: 'views/layouts/account/_base.html',
      controller: 'AccountController',
      controllerAs: 'viewModel',
    });
    $routeProvider.when('/domains/', {
      templateUrl: 'views/layouts/_domains.html',
      controller: 'DomainsController',
      controllerAs: 'viewModel',
    });
    $routeProvider.otherwise({
      redirectTo: '/'
    });
  }]);

})();
