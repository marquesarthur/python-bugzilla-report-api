'use strict';

var App = angular.module('report', [
    'ngRoute',
    'smart-table',
    'ngDialog'
]);

App.service('ReportService', function($http, $q) {
    var self = this;

    this.singleAssignee = undefined;

    this.backlog = undefined;

    this.backlogData = undefined;

    this.component = undefined;

    this.componentData = undefined;

    this.assignee = undefined;

    this.assigneeData = undefined;

    this.status = undefined;

    this.resolutions = undefined;

    window.backlog_callback = function(data) {
        self.backlog = data;
        console.log(self.backlog);
    };

    window.assignee_status_callback = function(data) {
        self.assignee = data;
        console.log(self.assignee);
    };
    
    window.assignee_resolution_callback = function(data) {
        self.assignee_resolution = data;
        console.log(self.assignee_resolution);
    };

    window.component_callback = function(data) {
        self.component = data;
        console.log(self.component);
    };

    window.resolutions_callback = function(data) {
        self.resolutions = data;
        console.log(self.resolutions);
    };

    window.status_callback = function(data) {
        self.status = data;
        console.log(self.status);
    };

    this.getJsonFile = function(file) {
        return $http.jsonp(file);
    };

    this.getBacklog = function() {
        return this.getJsonFile('../out/backlog.json?callback=JSON_CALLBACK');
    };

    this.getComponent = function() {
        return this.getJsonFile('../out/components.json?callback=JSON_CALLBACK');;
    };

    this.getAssigneeStatus = function() {
        return this.getJsonFile('../out/assignees_status.json?callback=JSON_CALLBACK');
    };

    this.getAssigneeResolution = function() {
        return this.getJsonFile('../out/assignees_resolution.json?callback=JSON_CALLBACK');
    };

    this.getResolutions = function() {
        return this.getJsonFile('../out/resolutions.json?callback=JSON_CALLBACK');
    };

    this.getStatus = function() {
        return this.getJsonFile('../out/status.json?callback=JSON_CALLBACK');
    };

    this.extractData = function() {
        this.getBacklog();
        this.getComponent();
        this.getAssigneeStatus();
        this.getAssigneeResolution();
        this.getStatus();
        this.getResolutions();
    };

    this.severities = function() {
        if (self.component === undefined) {
            return {};
        } else {
            return self.component[0].x;
        }
    };

    this.assigneeResolutions = function() {
        if (self.component === undefined) {
            return {};
        } else {
            return self.assignee[0].x;
        }
    };

    this.extractBacklogData = function() {
        console.log(">>>> extractBacklogData");
        var data = [];
        for (var i = 0; i < self.backlog.length; i++) {
            var bugStatus = self.backlog[i].name;
            var total = 0;
            for (var j = 0; j < self.backlog[i].y.length; j++) {
                total = total + self.backlog[i].y[j];
            }
            data.push({
                bugStatus: bugStatus,
                total: total
            });
        }
        self.backlogData = data;
        console.log(self.backlogData);
    };

    this.extractAssigneeResolutionData = function(mapKey) {
        console.log(">>>> extractAsigneeResolutionData");
        var data = [];

        for (var i = 0; i < self.assignee_resolution.length; i++) {
            var name = self.assignee_resolution[i].name;
            if (mapKey === name){
                self.singleAssignee = self.assignee_resolution[i];
            }
        }
        return undefined;
    };

    this.extractAssigneeData = function() {
        console.log(">>>> extractAssigneeData");
        var data = [];
        for (var i = 0; i < self.assignee.length; i++) {
            var name = self.assignee[i].name;
            var values = self.assignee[i].y;
            var total = 0;
            for (var j = 0; j < self.assignee[i].y.length; j++) {
                total = total + self.assignee[i].y[j];
            }
            data.push({
                name: name,
                total: total,
                values: values
            });
        }
        self.assigneeData = data;
        console.log(self.assigneeData);
    };

    this.extractComponentData = function() {
        console.log(">>>> extractComponentData");
        var data = [];
        for (var i = 0; i < self.component.length; i++) {
            var component = self.component[i].name;
            var values = self.component[i].y;
            var total = 0;
            for (var j = 0; j < self.component[i].y.length; j++) {
                total = total + self.component[i].y[j];
            }
            data.push({
                component: component,
                total: total,
                values: values
            });
        }
        self.componentData = data;
        console.log(self.componentData);
    };

});
App.controller('AssigneeController', function($scope, ReportService){
    var self = this;

    this.assignee = ReportService.singleAssignee;

    this.assigneeChart = function(){
        var lista = [];
        lista.push(self.assignee)
        Plotly.newPlot('bug-single-assignee-chart', lista);
    };
    
    this.assigneeData = function(){
        var data = {};
        var user_status = self.assignee.name;
        data.username = user_status.split("_")[0];
        data.status = user_status.split("_")[1];
        return data;
    };
});
App.controller('ReportController', function($scope, $http, $q, ReportService, ngDialog) {

    var self = this;

    this.loaded = false;

    $scope.backlog = function() {
        return ReportService.backlog;
    };

    $scope.component = function() {
        return ReportService.component;
    };

    $scope.assignee = function() {
        return ReportService.assignee;
    };

    $scope.status = function() {
        return ReportService.status;
    };

    $scope.resolutions = function() {
        return ReportService.resolutions;
    };

    $scope.severities = function() {
        return ReportService.severities();
    };

    $scope.assigneeResolutions = function(){
        return ReportService.assigneeResolutions();
    };

    $scope.loading = function() {
        var backlog = $scope.backlog() === undefined;
        var assignee = $scope.assignee() === undefined;
        var component = $scope.component() === undefined;
        var loading = backlog || assignee || component;
        if (!loading && !self.loaded) {
            self.loaded = true;
            ReportService.extractBacklogData();
            ReportService.extractComponentData();
            ReportService.extractAssigneeData();
        }
        return loading;
    };

    $scope.backlogChart = function() {
        Plotly.newPlot('bug-backlog-chart', $scope.backlog());
    };

    $scope.assigneeChart = function() {
        Plotly.newPlot('bug-assignee-chart', $scope.assignee());
    };

    $scope.componentChart = function() {
        Plotly.newPlot('bug-component-chart', $scope.component());
    };

    $scope.backlogData = function() {
        return ReportService.backlogData;
    };

    $scope.componentData = function() {
        return ReportService.componentData;
    };

    $scope.assigneeData = function() {
        return ReportService.assigneeData;
    };

    $scope.getAssigneeResolutionFor = function (name, index) {
        var assignee_resolution = name+'_'+$scope.assigneeResolutions()[index];
        ReportService.extractAssigneeResolutionData(assignee_resolution);
        ngDialog.open({ template: 'assignee.html', width: 1000, className: 'ngdialog-theme-default' });
    };

    $scope.rowCollection = [{
        firstName: 'Laurent',
        lastName: 'Renard',
        birthDate: new Date('1987-05-21'),
        balance: 102,
        email: 'whatever@gmail.com'
    }, {
        firstName: 'Blandine',
        lastName: 'Faivre',
        birthDate: new Date('1987-04-25'),
        balance: -2323.22,
        email: 'oufblandou@gmail.com'
    }, {
        firstName: 'Francoise',
        lastName: 'Frere',
        birthDate: new Date('1955-08-27'),
        balance: 42343,
        email: 'raymondef@gmail.com'
    }];

    (function main() {
        ReportService.extractData();
    })();
});

// App.config(function($routeProvider) {

//     $routeProvider.when("/", {
//         resolve: {
//             backlog: function(ReportService) {
//                 console.log("Resolving.... backlog");
//                 return ReportService.getBacklog();
//             }
//         }
//     });
// });