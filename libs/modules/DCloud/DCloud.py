#!/usr/bin/env python3
import logging
import sys
import zipfile
import shutil
import json

try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

import os

from libs.modules.BaseModule import BaseModule

logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Framework info: https://dcloud.io/

Reference:
1) https://uniapp.dcloud.net.cn/
2) https://dcloud.io/wap2app.html?platform=wap2app (not yet)
'''


class DCloud(BaseModule):
    def doSigCheck(self):
        if self.os == "android":
            return self._find_main_activity("io.dcloud.PandoraEntry")
        elif self.os == "ios":
            log.error("not support yet.")
            return False

        return False

    def doExtract(self, working_folder):

        # TODO:: should deliberately consider the relative path and absolute path
        extract_folder = os.path.join(os.getcwd(), working_folder, self.hash)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)
        tmp_folder = os.path.join(os.getcwd(), extract_folder, "tmp")
        os.makedirs(tmp_folder, exist_ok = True)

        # extract the assets/data/dcloud_control.xml to get appid
        zf = zipfile.ZipFile(self.detect_file, 'r')
        config_file = zf.extract("assets/data/dcloud_control.xml", tmp_folder)

        # parse the xml file, construct the path of app code, and extract
        appid = ""
        t = ET.ElementTree(file=config_file)
        for elem in t.iter(tag='app'):
            appid = elem.attrib['appid']

        # print(appid)
        code_dir = "assets/apps/{}/www/".format(appid)

        for f in zf.namelist():
            if f.startswith(code_dir):
                # print(f)
                # create dir anyway

                td = os.path.dirname(os.path.join(extract_folder, f[len(code_dir): ]))
                if not os.access(td, os.R_OK):
                    os.makedirs(td)
                with open(os.path.join(extract_folder, f[len(code_dir): ]), "wb") as fwh:
                    fwh.write(zf.read(f))

        # extracting the starting page
        j = json.load(open(os.path.join(extract_folder, "manifest.json"),'r'))

        self._dump_info(extract_folder, j['launch_path'])

        # clean env
        shutil.rmtree(tmp_folder)

        return extract_folder, j['launch_path']


def main():
    f = "../../../test_case/io.dcloud.PandoraEntry/09b6326e9e730e19383d93647bbc6910fb410b36.apk"
    dCloud = DCloud(f, "android")
    if dCloud.doSigCheck():
        logging.info("DCloud signature Match")

    extract_folder, launch_path = dCloud.doExtract("./working_folder")
    log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
