'use strict';

/* Controllers */

function IndexController($scope, $resource) {
  $scope.loginUser = function() {
    // var user = $resource(
    //   '/login',

    console.log('logging in user ' + $scope.email + ' : ' + $scope.password);
  }
}

function AboutController($scope) {

}

function DrugListController($scope, Drug) {
  var drugsQuery = Drug.get({}, function(drugs) {
    $scope.drugs = drugs.objects;
  });
}

function DrugDetailController($scope, $routeParams, Drug) {
  console.log('hi in drug detail');
  var drugQuery = Drug.get({drugId: $routeParams.drugId}, function(drug) {
    $scope.drug = drug;
  });
}
