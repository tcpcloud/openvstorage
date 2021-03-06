// Copyright 2014 Open vStorage NV
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
/*global define */
define([
    'jquery', 'knockout',
    'ovs/api'
], function($, ko, api) {
    "use strict";
    return function(guid) {
        var self = this;

        // Handles
        self.loadHandle = undefined;

        // Observables
        self.loading               = ko.observable(false);
        self.loaded                = ko.observable(false);
        self.guid                  = ko.observable(guid);
        self.name                  = ko.observable();
        self.ports                 = ko.observableArray([0, 0, 0]);
        self.clusterIP             = ko.observable();
        self.storageIP             = ko.observable();
        self.storageDriverID       = ko.observable();
        self.mountpoint            = ko.observable();
        self.mountpointTemp        = ko.observable();
        self.mountpointBFS         = ko.observable();
        self.mountpointMD          = ko.observable();
        self.mountpointReadCaches  = ko.observable();
        self.mountpointWriteCaches = ko.observable();
        self.mountpointFOC         = ko.observable();

        // Functions
        self.fillData = function(data) {
            self.name(data.name);
            self.ports(data.ports);
            self.clusterIP(data.cluster_ip);
            self.storageIP(data.storage_ip);
            self.storageDriverID(data.storageDriverID);
            self.mountpoint(data.mountpoint);
            self.mountpointTemp(data.mountpoint_temp);
            self.mountpointBFS(data.mountpoint_bfs);
            self.mountpointMD(data.mountpoint_md);
            self.mountpointReadCaches(data.mountpoint_readcaches);
            self.mountpointWriteCaches(data.mountpoint_writecaches);
            self.mountpointFOC(data.mountpoint_foc);
            self.loaded(true);
            self.loading(false);
        };
        self.load = function() {
            return $.Deferred(function(deferred) {
                self.loading(true);
                api.get('storagedrivers/' + self.guid())
                    .done(function(data) {
                        self.fillData(data);
                        deferred.resolve();
                    })
                    .fail(deferred.reject)
                    .always(function() {
                        self.loading(false);
                    });
            }).promise();
        }
    };
});
