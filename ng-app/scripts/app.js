var knownlyApp = angular.module('knownlyApp', [
  'ngRoute',
  'knownlyApp.services',
  'knownlyApp.controllers',
]);

knownlyApp.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/domains/', {
  	templateUrl: 'views/layouts/_domains.html',
  	controller: 'DomainsCtrl'
  });
  $routeProvider.otherwise({
  	redirectTo: '/domains/'
  });
}]);
