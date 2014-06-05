'use strict';

angular.module('SmacDB', ['ui.bootstrap', 'smacServices', 'smacFilters', 'ngResource', 'ngRoute'])
  .controller('landing', function($scope, $resource) {
    $scope.loginUser = function() {
      console.log('logging in user ' + $scope.email + ' : ' + $scope.password);
    }
  })
  .controller('about', function($scope) {
  })
  .controller('home', function($scope, $http, $location, limitToFilter) {
    $scope.showDrugList = true;
    $scope.handleSelection = function(item) {
      return $http.get('/drug_unique_id/' + item.type + '/' + item.name, {}).then(function(result) {
        console.log(result);
        $location.url('/drug/' + result.data.unique_id);
      });
    };
    $scope.getGenerics = function(val) {
      return $http.get('/api/typeahead-generics?q={"filters":[{"name":"label_name", "op":"is_null"}], "query":"' + val + '"}', {}).then(function(result) {
        return limitToFilter(result.data.objects, 10);
      });
    };
    $scope.getLabels = function(val) {
      return $http.get('/api/typeahead-labels?q={"filters":[{"name":"label_name", "op":"is_not_null"}], "query":"' + val + '"}', {}).then(function(result) {
        return limitToFilter(result.data.objects, 10);
      });
    };
    $http.get('/api/random-drugs?q={"number":10, "type":"generic_name"}', {}).then(function(result) {
      $scope.randomGenerics = result.data.objects;
    });
    $http.get('/api/random-drugs?q={"number":10, "type":"label_name"}', {}).then(function(result) {
      $scope.randomLabels = result.data.objects;
    });
  })
  .controller('drugDetail', function($scope, $routeParams, Drug) {
    var drugQuery = Drug.get({drug_id: $routeParams.drug_id}, function(drug) {
      $scope.drug = drug;
      $scope.drug.label_name = title(drug.label_name);
      $scope.drug.generic_name = title(drug.generic_name);
      $scope.hasProposed = drug.hasProposed;
      $scope.hasFUL = drug.hasFUL;
      $scope.hasForm = drug.hasForm;
      $scope.hasStrength = drug.hasStrength;
      $scope.hasLabelName = drug.label_name != null;
      $scope.shortList = true;
    });
  })
  .controller('drugList', function($scope, Drug) {
    var drugsQuery = Drug.get({}, function(drugs) {
      $scope.drugs = drugs.objects;
    });
  })
  .config([
    '$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {
      $routeProvider
	.when('/', {
	  templateUrl: 'static/partials/landing.html',
          controller: 'landing'
	})
	.when('/about', {
	  templateUrl: 'static/partials/about.html',
          controller: 'about'
	})
        .when('/drug', {
          templateUrl: '/static/partials/drug-list.html',
          controller: 'drugList'
        })
        .when('/drug/:drug_id', {
          templateUrl: '/static/partials/drug-detail.html',
          controller: 'drugDetail'
        })
        .when('/home', {
          templateUrl: 'static/partials/home.html',
          controller: 'home'
        })
	.otherwise({
	  redirectTo: '/'
	});
      $locationProvider.html5Mode(true);
    }
  ]);

var title = function(input) {
  // TODO: Get the filter version of this working instead
  var parts = input.toLowerCase().split(' ');
  for (var index in parts) {
    var part = parts[index];
    if (part == '') {
      continue;
    }
    parts[index] = part.slice(0, 1).toUpperCase() + part.slice(1);
  }
  return parts.join(' ');
}
