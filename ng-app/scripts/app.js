(function () {
  'use strict';

  var knownlyApp = angular.module('knownlyApp', [
    'autocomplete',
    'ngAnimate',
    'ngCookies',
    'ui.bootstrap',
    'ui.router',
    'analytics.mixpanel',
    'knownlyApp.services.account',
    'knownlyApp.services.authentication',
    'knownlyApp.services.domains',
    'knownlyApp.services.dropboxsite',
    'knownlyApp.services.vouchers',
    'knownlyApp.controllers.account',
    'knownlyApp.controllers.account.profile',
    'knownlyApp.controllers.account.billing',
    'knownlyApp.controllers.account.vouchers',
    'knownlyApp.controllers.console',
    'knownlyApp.controllers.createdropboxsiteform',
    'knownlyApp.controllers.domains',
    'knownlyApp.controllers.deletedropboxsitemodal',
    'knownlyApp.controllers.dropboxsitelist',
    'knownlyApp.controllers.navbar'
  ]);

  knownlyApp.constant('_', window._);

  knownlyApp.config(['$locationProvider', '$stateProvider', '$urlRouterProvider', '$httpProvider', '$mixpanelProvider',
    function($locationProvider, $stateProvider, $urlRouterProvider, $httpProvider, $mixpanelProvider) {

    var mixpanelToken = '/* @echo MIXPANEL_TOKEN */';
    $mixpanelProvider.apiKey(mixpanelToken);
    
    // Disable hash routing
    $locationProvider.hashPrefix('!');
    $locationProvider.html5Mode(true);
    
    // Use Django CSRF tokens
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';

    // Use $urlRouterProvider to configure any redirects (when) and invalid urls (otherwise).
    $urlRouterProvider
      .otherwise('/');

    $stateProvider
      .state('domains', {
        url: '/domains/',
        views: {
          'main': {
            templateUrl: 'components/domains/domains.html',
            controller: 'DomainsController',
            controllerAs: 'viewModel',
          }
        }
      })
      .state('account', {
        abstract: true,
        url: '/account/',
        views: {
          'main': {
            templateUrl: 'components/account/account.html',
            controller: 'AccountController',
            controllerAs: 'viewModel'            
          }
        }
      })
      .state('account.profile', {
        url: 'profile/',
        views: {
          'account-section': {
            templateUrl: 'components/profile/profile.html',
            controller: 'ProfileController',
            controllerAs: 'viewModel'            
          }
        }
      })
      .state('account.billing', {
        url: 'billing/',
        views: {
          'account-section': {
            templateUrl: 'components/billing/billing.html',
            controller: 'BillingController',
            controllerAs: 'viewModel'
          }
        }
      })
      .state('account.vouchers', {
        url: 'vouchers/',
        views: {
          'account-section': {
            templateUrl: 'components/vouchers/vouchers.html',
            controller: 'VouchersController',
            controllerAs: 'viewModel'
          }
        }
      })
      .state('console',{
        url: '/',
        views: {
          'main': {
            templateUrl: 'components/console/console.html',
            controller: 'ConsoleController',
            controllerAs: 'viewModel',
          }
        }
      });
  }]);
})();
