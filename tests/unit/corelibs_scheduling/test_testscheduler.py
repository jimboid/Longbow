# BSD 3-Clause License
#
# Copyright (c) 2017, Science and Technology Facilities Council and
# The University of Nottingham
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
This testing module contains the tests for the testscheduler method within the
scheduling module.
"""

try:

    from unittest import mock

except ImportError:

    import mock

import pytest

import longbow.corelibs.exceptions as exceptions
from longbow.corelibs.scheduling import _testscheduler


@mock.patch('longbow.corelibs.shellwrappers.sendtossh')
def test_testscheduler_detection1(mock_ssh):

    """
    Test that a handler can be detected. It is hard to specify exactly which
    to go for due to dictionaries being unordered.
    """

    job = {
        "modules": "",
        "resource": "test-machine",
        "handler": "",
        "scheduler": ""
    }

    mock_ssh.return_value = None

    _testscheduler(job)

    assert job["scheduler"] in ["lsf", "pbs", "sge", "soge", "slurm"]


@mock.patch('longbow.corelibs.shellwrappers.sendtossh')
def test_testscheduler_detection2(mock_ssh):

    """
    Test that a handler can be detected. It is hard to specify exactly which
    to go for due to dictionaries being unordered. Throw in a failure event.
    """

    job = {
        "modules": "",
        "resource": "test-machine",
        "handler": "",
        "scheduler": ""
    }

    mock_ssh.side_effect = [exceptions.SSHError("SSH Error", "Error"), None]

    _testscheduler(job)

    assert job["scheduler"] in ["lsf", "pbs", "sge", "soge", "slurm"]


@mock.patch('longbow.corelibs.shellwrappers.sendtossh')
def test_testscheduler_except(mock_ssh):

    """
    Test that the correct exception is raised when nothing can be detected.
    """

    job = {
        "modules": "",
        "resource": "test-machine",
        "handler": "",
        "scheduler": ""
    }

    mock_ssh.side_effect = exceptions.SSHError("SSH Error", "Error")

    with pytest.raises(exceptions.SchedulercheckError):

        _testscheduler(job)
