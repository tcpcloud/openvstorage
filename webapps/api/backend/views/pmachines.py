# Copyright 2014 Open vStorage NV
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
PMachine module
"""

from backend.decorators import required_roles, load, return_object, return_list, log, return_task
from backend.serializers.serializers import FullSerializer
from ovs.dal.hybrids.pmachine import PMachine
from ovs.dal.lists.pmachinelist import PMachineList
from ovs.lib.mgmtcenter import MgmtCenterController
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class PMachineViewSet(viewsets.ViewSet):
    """
    Information about pMachines
    """
    permission_classes = (IsAuthenticated,)
    prefix = r'pmachines'
    base_name = 'pmachines'

    @log()
    @required_roles(['read'])
    @return_list(PMachine)
    @load()
    def list(self):
        """
        Overview of all pMachines
        """
        return PMachineList.get_pmachines()

    @log()
    @required_roles(['read'])
    @return_object(PMachine)
    @load(PMachine)
    def retrieve(self, pmachine):
        """
        Load information about a given pMachine
        """
        return pmachine

    @log()
    @required_roles(['read', 'write', 'manage'])
    @load(PMachine)
    def partial_update(self, contents, pmachine, request):
        """
        Update a pMachine
        """
        contents = None if contents is None else contents.split(',')
        serializer = FullSerializer(PMachine, contents=contents, instance=pmachine, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action()
    @log()
    @required_roles(['read', 'write', 'manage'])
    @return_task()
    @load(PMachine)
    def configure_host(self, pmachine, request):
        """
        Configure the physical host
        """
        serializer = FullSerializer(PMachine, instance=pmachine, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return MgmtCenterController.configure_host.delay(pmachine.guid)

    @action()
    @log()
    @required_roles(['read', 'write', 'manage'])
    @return_task()
    @load(PMachine)
    def unconfigure_host(self, pmachine, request):
        """
        Unconfigure the physical host
        """
        serializer = FullSerializer(PMachine, instance=pmachine, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return MgmtCenterController.unconfigure_host.delay(pmachine.guid)
