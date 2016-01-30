'use strict';

/**
 * @ngdoc overview
 * @name yeomanApp
 * @description
 * # yeomanApp
 *
 * Main module of the application.
 */
angular
  .module('yeomanApp', [
    'ngRoute'
  ])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'static/main.html',
        controller: 'MainCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });

angular.module('yeomanApp')
  .controller('MainCtrl', function ($scope, $http) {
    $http.get('/api/new-item').then(
      function(result) {
        $scope.itemList = result['data']['items'] || [];
        // console.log(result);
      },
      function(err) {
        console.error(err);
      }
    )

    $scope.archive = function(id) {
      $http.post('/api/item/'+ id +'/archive').then(
        function(result) {
          // console.log('success archive');
          _.remove($scope.itemList, function(n) { return n['id'] == id; });
        });
    };
  });
