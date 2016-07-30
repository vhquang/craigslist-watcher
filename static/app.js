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

    function getItems() {
      $http.get('/api/new-item').then(
        function (result) {
          $scope.itemList = result['data']['items'] || [];
          // console.log(result);
        },
        function (err) {
          console.error(err);
        }
      );
    }

    getItems();

    $scope.archive = function(id) {
      $http.post('/api/item/'+ id +'/archive').then(
        function(result) {
          // console.log('success archive');
          _.remove($scope.itemList, function(n) { return n['id'] == id; });
        });
    };

    $scope.targetLink = '';
    $scope.scrapeLink = function(link) {
      if (!link) { return; }
      $scope.isLoading = true;
      $http.post('/api/scrape-link', {"link": link}).then(
        function(resp) { getItems(); },
        function (err) { console.error(err); },
        function (progress) { console.log(progress); }
      ).finally(
        function() { $scope.isLoading = false; }
      );
    }
  });
