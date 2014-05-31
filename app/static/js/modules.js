'use strict';

angular.module('SmacDB', ['smacServices', 'ngResource', 'ngRoute', 'typeahead'])
  .config([
    '$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {
      $routeProvider
	.when('/', {
	  templateUrl: 'static/partials/landing.html',
	  controller: IndexController
	})
	.when('/about', {
	  templateUrl: 'static/partials/about.html',
	  controller: AboutController
	})
        .when('/drug', {
          templateUrl: 'static/partials/drug-list.html',
          controller: DrugListController
        })
        .when('/drug/:drugId', {
          templateUrl: 'static/partials/drug-detail.html',
          controller: DrugDetailController
        })
        .when('/home', {
          templateUrl: 'static/partials/home.html',
          controller: HomeController
        })
	.otherwise({
	  redirectTo: '/'
	});
      $locationProvider.html5Mode(true);
    }
  ])
  .run(function($rootScope, $templateCache) {
    $rootScope.$on('$viewContentLoaded', function() {
      $templateCache.removeAll();
    });
  });