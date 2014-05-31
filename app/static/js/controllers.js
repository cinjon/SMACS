'use strict';

/* Controllers */

function IndexController($scope, $resource) {
  $scope.loginUser = function() {
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
  var drugQuery = Drug.get({drugId: $routeParams.drugId}, function(drug) {
    $scope.drug = drug;
  });
}

function HomeController($scope, typeaheadGenerics, typeaheadLabels, subscriptionQuery) {
  typeaheadGenerics.get({}, function(generics) {
    $scope.generics = generics;
    $scope.hideChoices = false;
  });
  typeaheadLabels.get({}, function(labels) {
    $scope.labels = labels;
    $scope.hideChoices = false;
  });
  subscriptionQuery.get({}, function(subscriptions) {
    $scope.subscriptions = subscriptions;
  });
}