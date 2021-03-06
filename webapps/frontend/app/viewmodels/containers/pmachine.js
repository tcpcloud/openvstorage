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
    'ovs/generic', 'ovs/api'
], function($, ko, generic, api) {
    "use strict";
    return function(guid) {
        var self = this;

        // Handles
        self.loadHandle  = undefined;

        // Observables
        self.edit           = ko.observable(false);
        self.loading        = ko.observable(false);
        self.loaded         = ko.observable(false);
        self.guid           = ko.observable(guid);
        self.name           = ko.observable();
        self.ipAddress      = ko.observable();
        self.hvtype         = ko.observable();
        self.mgmtCenterGuid = ko.observable();
        self.backupValue    = ko.observable();

        // Functions
        self.fillData = function(data) {
            if (!self.edit()) {
                self.name(data.name);
                self.hvtype(data.hvtype);
                self.ipAddress(data.ip);
                if (data.hasOwnProperty('mgmtcenter_guid')) {
                    self.mgmtCenterGuid(data.mgmtcenter_guid);
                }
            }
            self.loaded(true);
            self.loading(false);
        };
        self.load = function() {
            return $.Deferred(function(deferred) {
                self.loading(true);
                api.get('pmachines/' + self.guid())
                    .done(function(data) {
                        self.fillData(data);
                        deferred.resolve();
                    })
                    .fail(deferred.reject)
                    .always(function() {
                        self.loading(false);
                    });
            }).promise();
        };
        self.save = function() {
            return $.Deferred(function(deferred) {
                self.loading(true);
                api.patch('pmachines/' + self.guid(), {
                        data: {
                            name: self.name(),
                            mgmtcenter_guid: self.mgmtCenterGuid() === undefined ? null : self.mgmtCenterGuid(),
                            ip: self.ipAddress(),
                            hvtype: self.hvtype()
                        },
                        queryparams: { contents: 'mgmtcenter' }
                    })
                    .done(function() {
                        generic.alertSuccess(
                            $.t('ovs:pmachines.save.complete'),
                            $.t('ovs:pmachines.save.success', { what: self.name() })
                        );
                        self.loading(false);
                        deferred.resolve();
                    })
                    .fail(function(error) {
                        error = $.parseJSON(error.responseText);
                        generic.alertError(
                            $.t('ovs:generic.error'),
                            $.t('ovs:pmachines.save.failed', {
                                what: self.name(),
                                why: error.detail
                            })
                        );
                        self.loading(false);
                        deferred.reject();
                    });
            }).promise();
        };
    };
});
