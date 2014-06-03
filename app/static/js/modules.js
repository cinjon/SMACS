'use strict';

angular.module('SmacDB', ['ui.bootstrap', 'smacServices', 'ngResource', 'ngRoute'])
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
      console.log(result);
      $scope.randomLabels = result.data.objects;
    });
  })
  .controller('drugDetail', function($scope, $routeParams, Drug) {
    var drugQuery = Drug.get({drug_id: $routeParams.drug_id}, function(drug) {
      console.log(drug);
      $scope.drug = drug;
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

// angular.module("template/home/drug-result.html", []).run(["$templateCache", function($templateCache) {
//   $templateCache.put("template/home/drug-result.html",
//     "<ul class=\"dropdown-menu\" ng-style=\"{display: isOpen()&&'block' || 'none', width:100%, top: position.top+25+'px'}\">\n" +
//     "    <li ng-repeat=\"match in matches\" ng-class=\"{active: isActive($index) }\" ng-mouseenter=\"selectActive($index)\" ng-click=\"selectMatch($index)\">\n" +
//     "        <div typeahead-match index=\"$index\" match=\"match\" query=\"query\" template-url=\"templateUrl\"></div>\n" +
//     "    </li>\n" +
//     "</ul>");
// }]);
