/**
* Console controller
* @namespace knownlyApp.controllers
*/
(function () {
  'use strict';

  angular
    .module('knownlyApp.controllers.console', [])
    .controller('ConsoleController', ConsoleController);

  ConsoleController.$inject = [];

  /**
  * @namespace ConsoleController
  */
  function ConsoleController() {
    var viewModel = this;
  }
})();
