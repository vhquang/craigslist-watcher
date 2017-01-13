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

    $scope.trackingList = [];
    $scope.selectTracking = {};
    $scope.itemList = [];


    function getItems(trackingId) {
      $http.get('api/tracking/' + trackingId + '/item').then(
        function (result) {
          $scope.itemList = result['data']['items'] || [];
          // console.log(result);
        },
        function (err) {
          console.error(err);
        }
      );
    }

    function resetItemsResult() {
      $scope.itemList = [];
    }

    function getUserInfo() {
      $http.get('api/me').then(
        function(resp) {
          var user = resp.data || {};
          if (!!user['id']) { $scope.user = user; }
        },
        function(err) {
          console.error(err);
          alert('Cannot get user info');
        }
      );
    }

    $scope.getTrackingList = function() {
      $http.get('api/tracking').then(
        function(resp) {
          $scope.trackingList = resp.data.items || [];
        }
      );
    };

    $scope.saveTracking = function(tracking) {
      function _updateTrackingList(tracking) {
        var id = tracking['id'];
        for (var i = 0; i <= $scope.trackingList.length; i++) {
          if (i === $scope.trackingList.length) {
            $scope.trackingList.push(tracking);
            break;
          }
          if ($scope.trackingList[i]['id'] === id) {
            $scope.trackingList[i] = tracking;
            break;
          }
        }
        $scope.selectTracking = tracking;
      }

      var id = tracking['id'] || '';
      $http.post('api/tracking/' + id, tracking).then(
        function(resp) { _updateTrackingList(resp.data); },
        function(err) { console.error(err); }
      );
    };

    $scope.deleteTracking = function(id) {
      function _removeTracking(id) {
        // todo use lodash
        for (var i = 0; i < $scope.trackingList.length; i++) {
          if ($scope.trackingList[i]['id'] === id) {
            $scope.trackingList.splice(i, 1);
          }
        }
        $scope.clearTrackingItem();
      }

      $http.delete('api/tracking/' + id).then(
        function() { _removeTracking(id); },
        function(err) { console.error(err); alert('Cannot delete tracking link'); }
      );
    };

    $scope.selectTrackingItem = function(item) {
      $scope.selectTracking = item;
    };

    $scope.clearTrackingItem = function() {$scope.selectTracking = {}; }

    $scope.login = function() {
      location.href = 'api/login';
    };

    $scope.logout = function() {
      $http.post('api/logout').then(
        function() {},
        function() { console.error('Cannot logout'); }
      ).finally(function() { 
        $scope.user = null; 
      });
    };

    $scope.archive = function(trackingId, itemId) {
      $http.post('api/tracking/' + trackingId + '/item/'+ itemId +'/archive').then(
        function(result) {
          // console.log('success archive');
          _.remove($scope.itemList, function(n) { return n['id'] == itemId; });
        });
    };

    $scope.targetLink = '';
    $scope.scrapeLink = function(link) {
      if (!link) { return; }
      $scope.isLoading = true;
      // todo make sure tracking has id
      var trackingId = $scope.selectTracking['id'];
      $http.post('api/scrape-link', {"link": link, 'tracking_id': trackingId}).then(
        function(resp) { getItems(trackingId); },
        function (err) { console.error(err); alert('Cannot get items'); },
        function (progress) { console.log(progress); }
      ).finally(
        function() { $scope.isLoading = false; }
      );
    };

    $scope.matchDescription = function(description, query) {
      var words = (description || "").toLowerCase(),
        search = new Set( (query || "").toLowerCase().split(/\s/) );
      search.delete("");
      if (search.size === 0 || words.length === 0) {
        return false;
      }
      for (var i = 0, s = null; s = search[i]; i++) {
        if ( words.indexOf(s) < 0 ) { return false; }
      }
      return true;
    };

    getUserInfo();
    $scope.getTrackingList();

    $scope.$watch('user', function(val) {
      if ((val != null) && ('id' in val)) {

      } else {
        resetItemsResult();
      }
    });

    $scope.$watch('selectTracking', function(val) {
      if (val && !!val['id']) {
        getItems(val['id'])
      }
    });

    (function($window, element) {
      var initialTopPosition, initialWidth;
      setTimeout(function() {
        // without an immediate timeout, the offset.top is set as bottom
        // instead of top of the element
        initialTopPosition = $(".pinned").position().top;
        initialWidth = element.width();
      }, 0);
      $window.on('scroll', function() {
        var top = $window.scrollTop();
        if (initialTopPosition < top) {
          element.addClass("pinned-active");
          element.css("width", initialWidth);
        } else {
          element.css("width", "");
          element.removeClass("pinned-active");
        }
      });
    })( $(window), $(".pinned") );
  });
