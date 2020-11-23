#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import abc
import logging
import sys
import hashlib
import subprocess
import json
import os

from libs.modules import ModuleConfig

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

class BaseModule(metaclass=abc.ABCMeta):
    def __init__(self, detect_file, os):
        self.detect_file = detect_file
        self.os = os
        self.hash = self._gethash()

    def _dump_info(self, extract_folder, launch_path):
        info = {"detect_file": self.detect_file, "start_page": launch_path}
        json.dump(info, open(os.path.join(extract_folder, "extract_info.json"), 'w'))
        return

    # find signature
    def _find_main_activity(self, sig):
        proc = subprocess.Popen("'{}' dump badging '{}'".format(ModuleConfig.ModuleConfig["aapt"], self.detect_file), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        r = (proc.communicate()[0]).decode()
        # e = (proc.communicate()[1]).decode()
        # print(r)
        # print(e)
        if r.find(sig) != -1:
            return True
        return False

    def _gethash(self):
        with open(self.detect_file, "rb") as frh:
            sha1obj = hashlib.sha1()
            sha1obj.update(frh.read())
            return sha1obj.hexdigest()

    def __str__(self):
        return "{} file: {}".format(self.os, self.detect_file)

    @abc.abstractmethod
    def doSigCheck(self):
        pass

    @abc.abstractmethod
    def doExtract(self, working_folder):
        pass

