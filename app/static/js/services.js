'use strict';

angular.module('smacServices', ['ngResource'])
  .factory('Drug', function($resource) {
    return $resource('/api/drug/:drugId', {}, {
      query: {
	method: 'GET',
	params: {drugId:''},
	isArray: true
      }
    });
  })
  .factory('typeaheadGenerics', function($resource) { //TODO: limit this to not be regular accessible
    return $resource('/api/typeahead-generics?q={"filters":[{"name":"label_name", "op":"is_null"}]}', {}, {
      query: {
	method: 'GET',
	isArray: true
      }
    })
  })
  .factory('typeaheadLabels', function($resource) { //TODO: limit this to not be regular accessible
    return $resource('/api/typeahead-labels?q={"filters":[{"name":"label_name", "op":"is_not_null"}]}', {}, {
      query: {
	method: 'GET',
	isArray: true
      }
    })
  })
  .factory('subscriptionQuery', function($resource) {
    // Returns the current user's subscriptions
    return $resource('/api/subscriptions', {}, {
      query: {
        method: 'GET',
        isArray: true
      }
    })
  });
