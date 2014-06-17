'use strict';

var drugForms = ['tablet', 'capsule', 'cream', 'drops', 'suspension',
                 'vial', 'spray', 'ointment', 'lotion', 'syrup',
                 'syringe', 'elixir', 'gel', 'powder', 'piggyback',
                 'shampoo', 'other'];

angular.module('SmacDB', ['ui.bootstrap', 'smacServices', 'smacFilters', 'ngResource', 'ngRoute', 'highcharts-ng'])
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
      return $http.get('/drug-unique-id/' + item.type + '/' + item.name, {}).then(function(result) {
        $location.url('/drug/' + result.data.unique_id);
      });
    };
    $scope.getGenerics = function(val) {
      return $http.get('/typeahead/generic/' + val, {}).then(function(result) {
        return limitToFilter(result.data.objects, 10);
      });
    };
    $scope.getLabels = function(val) {
      return $http.get('/typeahead/label/' + val, {}).then(function(result) {
        return limitToFilter(result.data.objects, 10);
      });
    };
    $http.get('/get-random-drugs/generic/10', {}).then(function(result) {
      $scope.randomGenerics = result.data.data;
    });
    $http.get('/get-random-drugs/label/10', {}).then(function(result) {
      $scope.randomLabels = result.data;
    });
  })
  .controller('drugDetail', function($scope, $routeParams, Drug) {
    var drugQuery = Drug.get({drug_id: $routeParams.drug_id}, function(result) {
      var drug = result.drug;
      $scope.drug = drug;
      $scope.drug.label_name = title(drug.label_name);
      $scope.drug.generic_name = title(drug.generic_name);
      $scope.hasProposed = drug.hasProposed;
      $scope.hasFUL = drug.hasFUL;
      $scope.hasForm = drug.hasForm;
      $scope.hasStrength = drug.hasStrength;
      $scope.hasLabelName = (drug.label_name != null);

      $scope.strengths = _.uniq(drug.listings.map(function(listing) {return listing.strength}));
      $scope.strength = $scope.strengths[0];
      $scope.forms = _.uniq(drug.listings.map(function(listing) {return listing.form}));
      $scope.form = $scope.forms[0];

      var filteredList = filterByStrengthAndForm($scope.form, $scope.strength, drug.listings);
      $scope.strengthAndFormFilteredList = splitArrayHalf(filteredList);
      $scope.smacData = convertToData(filteredList, 'smac');
      $scope.fulData = convertToData(filteredList, 'ful');
      $scope.proposedData = convertToData(filteredList, 'proposed');

      $scope.getPrice = function(listing) {
        var price = '';
        if (listing.smac && listing.smac != '') {
          price += round(listing.smac, 2);
        }
        if (listing.proposed && listing.proposed != '') {
          price += ' ($' + round(listing.proposed, 2) + '*)';
        }
        return price.trim();
      }

      $scope.$watch('form', function(newValue, oldValue) {
        var filteredList = filterByStrengthAndForm(newValue, $scope.strength, drug.listings);
        $scope.strengthAndFormFilteredList = splitArrayHalf(filteredList);
        $scope.smacData = convertToData(filteredList, 'smac');
        $scope.fulData = convertToData(filteredList, 'ful');
        $scope.proposedData = convertToData(filteredList, 'proposed');
      });
      $scope.$watch('strength', function(newValue, oldValue) {
        var filteredList = filterByStrengthAndForm($scope.form, newValue, drug.listings);
        $scope.strengthAndFormFilteredList = splitArrayHalf(filteredList);
        $scope.smacData = convertToData(filteredList, 'smac');
        $scope.fulData = convertToData(filteredList, 'ful');
        $scope.proposedData = convertToData(filteredList, 'proposed');
      });

      $scope.drugChartConfig = {
        options: {
          chart: {
            type: 'spline'
          }
        },
        xAxis: {
          type: 'datetime',
          dateTimeLabelFormats: {
            day: '%b %e',
            week: '%b %e'
          },
          title: {
            text: 'Date'
          },
        },
        yAxis: {
          title: {
            text: 'Price ($)'
          },
          min: 0
        },
        series: [
          {
            name: 'State Maximum Acquired Cost',
            data: $scope.smacData
          },
          {
            name: 'Proposed',
            data: $scope.proposedData
          },
          {
            name: 'Federal Upper Limit',
            data: $scope.fulData
          }
        ],
        loading: false
      }
    });
  })
  .controller('edit', function($scope, $http, limitToFilter, filterFilter) {
    $scope.drugForms = capitalize_all(drugForms);
    $http.get('/get-edit-drugs').then(function(result) {
      $scope.drugs = result.data.objects;
      $scope.genericNames = get_field_from_drugs($scope.drugs, 'generic_name');
      $scope.labelNames = get_field_from_drugs($scope.drugs, 'label_name');
    });
    $http.get('/typeahead-canonical-names', {}).then(function(result) {
      $scope.canonicalNames = result.data.objects;
    });
    $scope.startsWith = function(canonicalName, viewValue) {
      return canonicalName.substr(0, viewValue.length).toUpperCase() == viewValue.toUpperCase();
    }
    $scope.submit = function(drug, index) {
      $http({
        url:'/edit-drug',
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        data: $.param(drug)
      }).success(function(data) {
        $scope.drugs.splice(index, 1);
        $scope.genericNames.splice(index, 1);
        $scope.labelNames.splice(index, 1);
        $scope.addToCanonicalNames(data, 'generic_name');
        $scope.addToCanonicalNames(data, 'label_name');
      });
    }
    $scope.addToCanonicalNames = function(data, key) {
      if (key in data && $scope.canonicalNames.indexOf(data[key]) > -1) {
        $scope.canonicalNames.push(data[key]);
      }
    }
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
        .when('/edit', {
          templateUrl: 'static/partials/edit.html',
          controller: 'edit'
        })
	.otherwise({
	  redirectTo: '/'
	});
      $locationProvider.html5Mode(true);
    }
  ]);

var title = function(input) {
  // TODO: Get the filter version of this working instead
  if (!input) {
    return null;
  }
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

var capitalize_all = function(arr) {
  return drugForms.map(function(form) {
    return form.slice(0, 1).toUpperCase() + form.slice(1);
  });
}

var get_field_from_drugs = function(drugs, field) {
  return drugs.map(function(drug) {
    return drug[field];
  });
}

var splitArrayHalf = function(arr) {
  var len = arr.length;
  var ret = [];
  var i = 0;
  var number = 2;
  while (i < len) {
    var size = Math.ceil((len - i) / number--);
    ret.push(arr.slice(i, i += size));
  }
  return ret;
}

var filterByStrengthAndForm = function(form, strength, listings) {
  return listings.filter(function(listing) {
    return listing.form == form && listing.strength == strength;
  });
}

var convertToData = function(listings, key) {
  console.log(listings[0].effective_date);
  return listings.map(function(listing) {
    var date = listing.effective_date;
    return [Date.UTC(date[2], date[1], date[0]), listing[key]];
  });
}