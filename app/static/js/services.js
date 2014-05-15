'use strict';

angular.module('smacServices', ['ngResource'])
  .factory('Drug', function($resource) {
    console.log('hi in asking api for drugId');
    return $resource('/api/drug/:drugId', {}, {
      query: {
	method: 'GET',
	params: {drugId:''},
	isArray: true
      }
    });
  });