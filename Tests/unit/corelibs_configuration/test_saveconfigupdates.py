# Longbow is Copyright (C) of James T Gebbie-Rayet and Gareth B Shannon 2015.
#
# This file is part of the Longbow software which was developed as part of the
# HECBioSim project (http://www.hecbiosim.ac.uk/).
#
# HECBioSim facilitates and supports high-end computing within the UK
# biomolecular simulation community on resources such as ARCHER.
#
# Longbow is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Longbow is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Longbow.  If not, see <http://www.gnu.org/licenses/>.

"""
This testing module contains the tests for the configuration module methods.
"""

import Longbow.corelibs.configuration as conf


def test_saveconfigupdates_test1():

    """
    Simple test to check if the updates are applied.
    """

    contents = ["[test1]", "param1 = 2", "param2 = test", "param3 = true",
                "[test2]", "parama = f", "paramb = 12",
                "paramc = /path/to/somethingelse"]

    valuediff = {
        "test1": {
            "param1": "1"
        },
        "test2": {
            "paramb": "1293",
            "paramc": "/path/to/something"
        }
    }

    oldparams = {
        "test1": {
            "param1": "2",
            "param2": "test",
            "param3": "true"
        },
        "test2": {
            "parama": "f",
            "paramb": "12",
            "paramc": "/path/to/somethingelse"
        }
    }

    conf._saveconfigupdates(contents, oldparams, valuediff)

    assert contents == ["[test1]", "param1 = 1", "param2 = test",
                        "param3 = true", "[test2]", "parama = f",
                        "paramb = 1293", "paramc = /path/to/something"]


def test_saveconfigupdates_test2():

    """
    Simple test to check if the updates are applied.
    """

    contents = ["[test1]", "param1=2", "param2=test", "param3=true", "[test2]",
                "parama=f", "paramb=12", "paramc=/path/to/somethingelse"]

    valuediff = {
        "test1": {
            "param1": "1"
        },
        "test2": {
            "paramb": "1293",
            "paramc": "/path/to/something"
        }
    }

    oldparams = {
        "test1": {
            "param1": "2",
            "param2": "test",
            "param3": "true"
        },
        "test2": {
            "parama": "f",
            "paramb": "12",
            "paramc": "/path/to/somethingelse"
        }
    }

    conf._saveconfigupdates(contents, oldparams, valuediff)

    assert contents == ["[test1]", "param1 = 1", "param2=test", "param3=true",
                        "[test2]", "parama=f", "paramb = 1293",
                        "paramc = /path/to/something"]
