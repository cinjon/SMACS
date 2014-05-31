angular.module('typeahead', [])
  .factory('dataFactory', function($http) {
    return {
      get: function(url) {
        return $http.get(url).then(function(resp) {
          return resp.data;
        })
      }
    }
  })
  .controller('typeaheadController', function($scope, dataFactory) { // DI in action
    // Get the parent scope and put parent.$scope.items here as $scope.items
    // Instead of using dataFactory that is.
    // Do the same for parent.$scope.hideChoices
    $scope.displayLimit = 3;
    dataFactory.get('static/drugTestLimit.json').then(function(data) {
      $scope.items = data;
    });
    $scope.name = ''; // This will hold the selected item
    $scope.onItemSelected = function() { // this gets executed when an item is selected
      console.log('url = ' + $scope.url);
      console.log('selected =' + $scope.name);
    };
  })
  .directive('typeahead', function($timeout) {
    return {
      restrict: 'AEC',
      scope: {
        items: '=',
        prompt: '@',
        title: '@',
        subtitle: '@',
        id: '@',
        model: '=',
        onSelect: '&'
      },
      link: function(scope, elem, attrs) {
        scope.handleSelection = function(selectedItem) {
          scope.model = selectedItem;
          scope.current = 0;
          scope.selected = true;
          $timeout(function() {
            scope.onSelect();
          }, 200);
        };
        scope.current = 0;
        scope.isCurrent = function(index) {
          return scope.current == index;
        };
        scope.setCurrent = function(index) {
          scope.current = index;
        };
      },
      templateUrl: 'static/partials/typeahead.html'
    };
  });