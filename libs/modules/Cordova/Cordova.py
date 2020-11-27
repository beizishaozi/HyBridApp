#!/usr/bin/env python3

import logging
import sys
import zipfile
import shutil


try:
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

import os
from libs.modules.BaseModule import BaseModule
'''reference libs modules need to put the directory of this project in $path variable'''


logging.basicConfig(stream=sys.stdout, format="%(levelname)s: %(message)s", level=logging.INFO)
log = logging.getLogger(__name__)

'''
Reference:
1) http://cordova.axuer.com/docs/zh-cn/latest/guide/support/index.html
'''

# extracting the starting page from "res/xml/config.xml" in "<content src="index.html" />"
def extract_start_page_by_aapt(apkfile, xmlfile, outputfile):
    launchpath = "nothing"
    command = 'aapt dump xmltree %s %s > %s' % (apkfile, xmlfile, outputfile)  #extract tree format from Android binary xml
    if os.system(command) != 0:
        print('fail:', command)
        return launchpath
    file = open(outputfile)
    line = file.readline()
    while line:
        if line.find("E: :content") > 0:
            line = file.readline()
            if line.find("A: src=\"") > 0:
                a = line[line.index("A: src=\"")+8:]
                launchpath = a[:a.index("\"")]
                break
        line = file.readline()
    file.close()
    os.remove(outputfile)
    return launchpath

class Cordova(BaseModule):
    def doSigCheck(self):
        if self.os == "android":
            return self._find_main_activity("org.apache.cordova.CordovaActivity")
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

        #
        code_dir = "assets/www/"
        configxml = "res/xml/config.xml"
        launch_path = ""

        for f in zf.namelist():
            if f.startswith(code_dir):
                # print(f)
                # create dir anyway

                td = os.path.dirname(os.path.join(extract_folder, f[len(code_dir): ]))
                if not os.access(td, os.R_OK):
                    os.makedirs(td)
                with open(os.path.join(extract_folder, f[len(code_dir): ]), "wb") as fwh:
                    fwh.write(zf.read(f))
            elif f == configxml:
                outputconfigfile = os.path.join(extract_folder, "config.xml")
                os.mknod(outputconfigfile)  #create file named newconfig "/home/user/IdeaProjects/HyBridApp/libs/modules/Cordova/working_folder/b54f2fdf0134405f35cbb6deba5ca7d62c9ae726/config.xml"
                print(os.path.dirname(f))
                # extracting the starting page from "res/xml/config.xml" in "<content src="index.html" />"
                launch_path = extract_start_page_by_aapt(self.detect_file, configxml, outputconfigfile)
                #launch_path = extract_start_page_by_axmlprinter(zf.extract(f), outputconfigfile)

        # clean env
        shutil.rmtree(tmp_folder)
        return extract_folder, launch_path


def main():
    f = "../../../test_case/cordova.apk"
    cordova = Cordova(f, "android")
    if cordova.doSigCheck():
        logging.info("cordova signature Match")

    extract_folder, launch_path = cordova.doExtract("working_folder")
    log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
