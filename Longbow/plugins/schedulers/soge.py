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
This module contains the code to interact with the various flavours of
Son of Grid Engine.

delete(host, job)
    A method for deleting a single job.

prepare(hosts, jobname, jobs)
    The method for creating the job submission file for a single job.

status(host, jobid)
    The method for checking the status of a job.

submit(hosts, jobname, jobs)
    The method for submitting a single job.
"""

import math
import os
import re

try:

    EX = __import__("corelibs.exceptions", fromlist=[''])
    SHELLWRAPPERS = __import__("corelibs.shellwrappers", fromlist=[''])

except ImportError:

    EX = __import__("Longbow.corelibs.exceptions", fromlist=[''])
    SHELLWRAPPERS = __import__("Longbow.corelibs.shellwrappers", fromlist=[''])

QUERY_STRING = "env | grep -i 'sge'"


def delete(host, job):

    """
    Method for deleting job.
    """

    jobid = job["jobid"]

    try:

        shellout = SHELLWRAPPERS.sendtossh(host, ["qdel " + jobid])

    except EX.SSHError:

        raise EX.JobdeleteError("Unable to delete job.")

    return shellout[0]


def prepare(hosts, jobname, jobs):

    """
    Create the SGE jobfile ready for submitting jobs.
    """

    # Open file for SGE script.
    sgefile = os.path.join(jobs[jobname]["localworkdir"], "submit.sge")
    jobfile = open(sgefile, "w+")

    # Write the PBS script
    jobfile.write("#!/bin/bash --login\n"
                  "#$ -cwd -V\n")

    if jobname is not "":

        jobfile.write("#$ -N " + jobname + "\n")

    if jobs[jobname]["queue"] is not "":

        jobfile.write("#$ -q " + jobs[jobname]["queue"] + "\n")

    # Account to charge (if supplied).
    if hosts[jobs[jobname]["resource"]]["account"] is not "":

        # if no accountflag is provided use the default
        if hosts[jobs[jobname]["resource"]]["accountflag"] is "":

            jobfile.write("#$ -A " +
                          hosts[jobs[jobname]["resource"]]["account"] + "\n")
        # else use the accountflag provided
        else:

            jobfile.write("#$ " +
                          hosts[jobs[jobname]["resource"]]["accountflag"] +
                          " " + hosts[jobs[jobname]["resource"]]["account"] +
                          "\n")

    jobfile.write("#$ -l h_rt=" + jobs[jobname]["maxtime"] + ":00\n")

    # Job array
    if int(jobs[jobname]["replicates"]) > 1:

        jobfile.write("#$ -t 1-" + jobs[jobname]["replicates"] + "\n")

    cores = jobs[jobname]["cores"]
    cpn = hosts[jobs[jobname]["resource"]]["corespernode"]

    # Load levelling override. In cases where # of cores is less than
    # corespernode, user is likely to be undersubscribing.
    if int(cores) < int(cpn):

        cpn = cores

    # Calculate the number of nodes.
    nodes = float(cores) / float(cpn)

    # Makes sure nodes is rounded up to the next highest integer.
    nodes = str(int(math.ceil(nodes)))

    # Number of cpus per node (most machines will charge for all available cpus
    # per node whether you are using them or not)
    # ncpus = cpn

    # Number of mpi processes per node.
    # mpiprocs = cpn

    tmp = "nodes=" + nodes

    # Write the resource requests
    jobfile.write("#$ -l " + tmp + "\n")

    jobfile.write("#$ -pe ib " + cores + "\n\n")

    if jobs[jobname]["modules"] is not "":

        for module in jobs[jobname]["modules"].split(","):

            module = module.replace(" ", "")
            jobfile.write("module load {0}\n\n" .format(module))

    mpirun = hosts[jobs[jobname]["resource"]]["handler"]

    # Single job
    if int(jobs[jobname]["replicates"]) == 1:

        jobfile.write(mpirun + " " + jobs[jobname]["executableargs"] + "\n")

    # Job array
    elif int(jobs[jobname]["replicates"]) > 1:

        jobfile.write("cd rep${SGE_TASK_ID}/\n" +
                      mpirun + jobs[jobname]["executableargs"] + "\n")

    # Close the file (housekeeping)
    jobfile.close()

    # Append lsf file to list of files ready for staging.
    jobs[jobname]["upload-include"] = (
        jobs[jobname]["upload-include"] + ", submit.sge")
    jobs[jobname]["subfile"] = "submit.sge"


def status(host, jobid):

    """
    Method for querying job.
    """

    states = {
        "h": "Held",
        "qw": "Queued",
        "r": "Running"
        }

    jobstate = ""

    try:

        shellout = SHELLWRAPPERS.sendtossh(host, ["qstat -u " + host["user"]])

    except EX.SSHError:

        raise

    # PBS will return a table, so split lines into a list.
    stdout = shellout[0].split("\n")

    # Now match the jobid against the list of jobs, extract the line and split
    # it into a list
    job = [line for line in stdout if jobid in line][0].split()

    # Look up the job state and convert it to Longbow terminology.
    try:

        jobstate = states[job[4]]

    except KeyError:

        jobstate = "Finished"

    return jobstate


def submit(host, jobname, jobs):

    """
    Method for submitting a job.
    """

    # Set the path to remoteworkdir/jobnamexxxxx
    path = jobs[jobname]["destdir"]

    # Change into the working directory and submit the job.
    cmd = ["cd " + path + "\n",
           "qsub " + jobs[jobname]["subfile"]]

    # Process the submit
    try:

        shellout = SHELLWRAPPERS.sendtossh(host, cmd)

    except EX.SSHError:

        raise EX.JobsubmitError(
            "Something went wrong when submitting. The following output "
            "came back from the SSH call:\nstdout: {0}\nstderr {1}"
            .format(shellout[0], shellout[1]))

    try:

        # Do the regex in Longbow rather than in the subprocess.
        jobid = re.search(r'\d+', shellout[0]).group()

    except AttributeError:

        raise EX.JobsubmitError(
            "Could not detect the job id during submission, this means that "
            "either the submission failed in an unexpected way, or that "
            "Longbow could not understand the returned information.")

    # Put jobid into the job dictionary.
    jobs[jobname]["jobid"] = jobid
