/* Filters */
round = function(input, precision) {
  return input ?
    parseFloat(input).toFixed(precision) :
    "";
}

angular.module('smacFilters', [])
  .filter('prettifyDate', function() {
    return function(date) {
      return new Date(date).toDateString('yyyy-MM-dd');
    }
  })
  .filter('uppercase', function() {
    return function(input) {
      return input.toUpperCase();
    }
  })
  .filter('title', function() {
    return function(input) {
      console.log(input);
      parts = input.toLowerCase().split(' ');
      for (var index in parts) {
        part = parts[index];
        if (part == '') {
          continue;
        }
        parts[index] = part.slice(0, 1).toUpperCase() + part.slice(1);
      }
      return parts.join(' ');
    }
  })
  .filter("round", function () {
    return function(input, precision) {
      return round(input, precision);
    };
  })
  .filter("dollars", function () {
    return function(input) {
      if (input.slice(0, 1) != '(') {
        return input ? "$" + input : "";
      }
      return input;
    };
  });