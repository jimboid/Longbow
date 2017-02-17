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
This testing module contains basic testing for the LAMMPS plugin.
"""

import Longbow.apps.lammps as lammps


def test_subdict_test1():

    """
    Test substitutions of the form -var
    """

    args = ["-var", "myvar", "mydata", "-i", "example.in", "-l", "output"]

    subs = lammps.detectsubstitutions(args)

    assert isinstance(subs, dict)
    assert subs["myvar"] == "mydata"
    assert args == ["-i", "example.in", "-l", "output"]


def test_subdict_test2():

    """
    Test substitutions of the form -v
    """

    args = ["-v", "p", "myprot", "-i", "example.in", "-l", "output"]

    subs = lammps.detectsubstitutions(args)

    assert isinstance(subs, dict)
    assert subs["p"] == "myprot"
    assert args == ["-i", "example.in", "-l", "output"]