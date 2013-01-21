angular.module('highscoreServices', ['ngResource']).
    factory('User', function($resource){
        return $resource('api/user/:userId', {}, {
        });
    });

angular.module('highscore', ['highscoreServices']).
    config(function($routeProvider) {
        $routeProvider.
        when('/', {controller:HighscoreCtrl, templateUrl:'fragments/highscore.html'}).
        when('/user/:userId', {controller:UserCtrl, templateUrl:'fragments/user.html'}).
        otherwise({redirectTo:'/'});
    });

function UserCtrl($scope, $routeParams, User) {
    $scope.user = User.get({userId: $routeParams.userId});
}

function HighscoreCtrl($scope, $routeParams, User) {
    $scope.users = User.query()
}
