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
  });