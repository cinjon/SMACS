'use strict';

angular.module('smacServices', ['ngResource'])
  .factory('Drug', function($resource) {
    return $resource('/get-drug/:drug_id', {}, {
      query: {
	method: 'GET',
	params: {drug_id:''},
	isArray: true
      }
    });
  })
  .factory('subscriptionQuery', function($resource) {
    // Returns the current user's subscriptions
    return $resource('/subscriptions', {}, {
      query: {
        method: 'GET',
        isArray: true
      }
    })
  });
