# coding: utf-8

from __future__ import division, print_function, unicode_literals, absolute_import

"""
This module defines firetasks for running lammps
"""

import os
import shutil

from pymatgen.io.lammps.utils import PackmolRunner, LammpsRunner

from fireworks import explicit_serialize, FiretaskBase

from atomate.utils.utils import get_logger

__author__ = 'Kiran Mathew'
__email__ = "kmathew@lbl.gov"

logger = get_logger(__name__)


@explicit_serialize
class RunPackmol(FiretaskBase):
    """
    Run packmol.

    Required params:
        molecules (list): list of constituent molecules(Molecule objects)
        packing_config (list): list of dict config settings for each molecule in the
            molecules list. eg: config settings for a single moelcule
            [{"number": 1, "inside box":[0,0,0,100,100,100]}]

    Optional params:
        tolerance (float): packmol tolerance
        filetype (string): input/output structure file type
        control_params: packmol control parameters dictionary. Basically all parameters other
            than structure/atoms
        output_file: output file name. The extension will be adjusted according to the filetype
    """

    required_params = ["molecules", "packing_config"]
    optional_params = ["tolerance", "filetype", "control_params", "output_file"]

    def run_task(self, fw_spec):
        pmr = PackmolRunner(self["molecules"], self["packing_config"],
                            tolerance=self.get("tolerance", 2.0), filetype=self.get("filetype", "xyz"),
                            control_params=self.get("control_params", {"nloop": 1000}),
                            output_file=self.get("output_file", "packed_mol.xyz"))
        logger.info("Running packmol")
        pmr.run()
        logger.info("Packmol finished running.")


@explicit_serialize
class RunLammpsDirect(FiretaskBase):
    """
    Run LAMMPS directly (no custodian).

    Required params:
        lammsps_cmd (str): lammps command to run sans the input file name
    """

    required_params = ["lammps_cmd", "input_filename"]

    def run_task(self, fw_spec):
        lammps_cmd = self["lammps_cmd"]
        input_filename = self["input_filename"]
        lmps_runner = LammpsRunner(input_filename, lammps_cmd)
        stdout, stderr = lmps_runner.run()
        logger.info("LAMMPS finished running: {} \n {}".format(stdout, stderr))


@explicit_serialize
class RunLammpsFake(FiretaskBase):
    """
    Pretend run i.e just copy files from existing run dir.

    Required params:
        ref_dir (str): path to the reference dir
    """

    required_params = ["ref_dir"]

    def run_task(self, fw_spec):
        output_dir = os.path.abspath(self["ref_dir"])
        for file_name in os.listdir(output_dir):
            full_file_name = os.path.join(output_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.getcwd())
        logger.info("ran fake LAMMPS")
