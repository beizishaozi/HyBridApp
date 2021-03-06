#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import logging
import shutil
import os
import json

from libs.modules.APICloud.uzmap_resource_extractor import tools
from libs.modules.BaseModule import BaseModule

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: http://www.apicloud.com/video_play/2_5

Reference:
https://github.com/newdive/uzmap-resource-extractor
'''

class APICloud(BaseModule):

    def doSigCheck(self):
        if self.os == "android":
            return self._find_main_activity("com.uzmap.pkg.LauncherUI")
        elif self.os == "ios":
            log.error("not support yet.")
            return False
        return False


    def doExtract(self, working_folder):

        extract_folder = os.path.join(os.getcwd(), working_folder, self.hash)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        #os.makedirs(extract_folder, exist_ok = True)

        # https://github.com/newdive/uzmap-resource-extractor
        extractMap = tools.decryptAndExtractAPICloudApkResources(self.detect_file, extract_folder, printLog=True)

        # parse the xml file, construct the path of app code, and extract
        launch_path = ""
        t = ET.ElementTree(file=os.path.join(extract_folder, "config.xml"))
        for elem in t.iter(tag='content'):
            launch_path = elem.attrib['src']

        self._dump_info(extract_folder, launch_path)

        return extract_folder, launch_path


def main():

    f = "../../../test_case/APICloud.apk"
    apiCloud = APICloud(f, "android")
    if apiCloud.doSigCheck():
        logging.info("APICloud signature Match")

    extract_folder, launch_path = apiCloud.doExtract("./working_folder")
    log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
