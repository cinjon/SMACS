'use strict';

/* Controllers */

function IndexController($scope) {

}

function AboutController($scope) {

}

function DrugListController($scope, Drug) {
  console.log('hi in druglist')
  var drugsQuery = Drug.get({}, function(drugs) {
    $scope.drugs = drugs.objects;
  });
  console.log($scope.drugs);
}

function DrugDetailController($scope, $routeParams, Drug) {
  console.log('hi in drug detail');
  var drugQuery = Drug.get({drugId: $routeParams.drugId}, function(drug) {
    $scope.drug = drug;
  });
}
