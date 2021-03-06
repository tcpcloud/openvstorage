# Copyright 2015 Open vStorage NV
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Debian Package module
"""

import time
from ovs.log.logHandler import LogHandler
from subprocess import check_output
from subprocess import CalledProcessError

logger = LogHandler.get('lib', name='packager')


class DebianPackage(object):
    """
    Contains all logic related to Debian packages (used in e.g. Debian, Ubuntu)
    """

    OVS_PACKAGE_NAMES = ['openvstorage', 'openvstorage-backend', 'volumedriver-server', 'volumedriver-base', 'alba', 'openvstorage-sdm']
    APT_CONFIG_STRING = '-o Dir::Etc::sourcelist="sources.list.d/ovsaptrepo.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"'

    @staticmethod
    def _get_version(package_name):
        return check_output("dpkg -s {0} | grep Version | cut -d ' ' -f 2".format(package_name), shell=True).strip()

    @staticmethod
    def get_versions():
        versions = {}
        for package_name in DebianPackage.OVS_PACKAGE_NAMES:
            version_info = DebianPackage._get_version(package_name)
            if version_info:
                versions[package_name] = version_info
        return versions

    @staticmethod
    def install(package_name, client, force=False):
        force_text = '--force-yes' if force is True else ''
        counter = 0
        max_counter = 3
        while True and counter < max_counter:
            counter += 1
            try:
                client.run('apt-get install -y {0} {1}'.format(force_text, package_name))
                break
            except CalledProcessError as cpe:
                logger.warning('Install failed, trying again. Error: {0}'.format(cpe.output))
                if cpe.output and 'You may want to run apt-get update' in cpe.output[0]:
                    DebianPackage.update(client)
                if counter == max_counter:
                    raise cpe
            except Exception as ex:
                raise ex
            time.sleep(1)

    @staticmethod
    def update(client):
        counter = 0
        max_counter = 3
        while True and counter < max_counter:
            counter += 1
            try:
                client.run('apt-get update {0}'.format(DebianPackage.APT_CONFIG_STRING))
                break
            except CalledProcessError as cpe:
                logger.warning('Update failed, trying again. Error: {0}'.format(cpe.output))
                if counter == max_counter:
                    raise cpe
            time.sleep(1)

    @staticmethod
    def verify_update_required(packages, services, client):
        services_checked = []
        update_info = {'version': '',
                       'packages': [],
                       'services': []}
        for package_name in packages:
            installed = None
            candidate = None
            for line in client.run('apt-cache policy {0} {1}'.format(package_name, DebianPackage.APT_CONFIG_STRING)).splitlines():
                line = line.strip()
                if line.startswith('Installed:'):
                    installed = line.lstrip('Installed:').strip()
                elif line.startswith('Candidate:'):
                    candidate = line.lstrip('Candidate:').strip()

                if installed is not None and candidate is not None:
                    break

            if installed != '(none)' and candidate != installed:
                update_info['packages'].append(package_name)
                update_info['services'] = services
                update_info['version'] = candidate
            else:
                for service in services:
                    if service in services_checked:
                        continue
                    services_checked.append(service)
                    if client.file_exists('/opt/OpenvStorage/run/{0}.version'.format(service)):
                        running_version = client.file_read('/opt/OpenvStorage/run/{0}.version'.format(service)).strip()
                        if running_version != candidate:
                            update_info['services'].append(service)
                            update_info['version'] = candidate
        return update_info
