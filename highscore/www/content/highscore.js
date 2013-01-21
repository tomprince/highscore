angular.module('highscoreServices', ['ngResource']).
    factory('User', function($resource) {
      return $resource('api/user/:userId');
    }).
    factory('Events', function() {
      var source = new EventSource('api/events');
      return {
        listen: function (scope, msg) {
          source.addEventListener(msg, function(e) {
            scope.$broadcast(msg, JSON.parse(e.data));
          }, false)
        }
      };
    });

angular.module('highscore', ['highscoreServices']).
    config(function($routeProvider) {
        $routeProvider.
        when('/', {controller:HighscoreCtrl, templateUrl:'fragments/highscore.html'}).
        when('/user/:userId', {controller:UserCtrl, templateUrl:'fragments/user.html'}).
        otherwise({redirectTo:'/'});
    });

function UserCtrl($scope, $routeParams, User, Events) {
    $scope.user = User.get({userId: $routeParams.userId});
    msg = 'points.add';
    Events.listen($scope, msg);
    $scope.$on(msg, function (s, msg) {
      if (msg.userid == $routeParams.userId) {
        $scope.user.points.push({
          when: Date.now()/1000,
          points: msg.points,
          comments: msg.comments
        });
	$scope.$apply();
      }
    });
}

function HighscoreCtrl($scope, $routeParams, User, Events) {
    $scope.users = User.query()
    Events.listen($scope, 'points.add');
    $scope.$on('points.add', function (s, msg) {
      $scope.users = User.query()
    })
}
