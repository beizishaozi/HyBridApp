#!/usr/bin/env python3

import logging
import sys
import jpype
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
1) http://newdocx.appcan.cn/quickstart/create-app   //username=984363019@qq.com passwd=beizishaozi
'''

class Appcan(BaseModule):
    def doSigCheck(self):
        if self.os == "android":
            return self._find_main_activity("org.apache.cordova.CordovaActivity")
        elif self.os == "ios":
            log.error("not support yet.")
            return False

        return False

    def extractFromHybridApp(self, working_folder):
        extract_folder = os.path.join(os.getcwd(), working_folder, self.hash)
        if os.access(extract_folder, os.R_OK):
            shutil.rmtree(extract_folder)
        os.makedirs(extract_folder, exist_ok = True)

        # extract the assets/data/dcloud_control.xml to get appid
        zf = zipfile.ZipFile(self.detect_file, 'r')

        code_dir = "assets/widget/"
        for f in zf.namelist():
            if f.startswith(code_dir):
                # print(f)
                # create dir anyway

                td = os.path.dirname(os.path.join(extract_folder, f[len(code_dir): ]))
                if not os.access(td, os.R_OK):
                    os.makedirs(td)
                with open(os.path.join(extract_folder, f[len(code_dir): ]), "wb") as fwh:
                    fwh.write(zf.read(f))
        return extract_folder

    def decrypt(self, targetDir, key):
        print(key)

    def doExtract(self, targetapk):
        # 加载刚才打包的jar文件
        jarpath = os.path.join("../../bin/decodeAppcan_jar/decodeAppcan.jar")
        jarpath2 = os.path.join("../../bin/decodeAppcan_jar/kxml2-2.3.0.jar")
        jarpath3 = os.path.join("../../bin/decodeAppcan_jar/xmlpull-1.1.3.1.jar")
        jarpath4 = os.path.join("../../bin/decodeAppcan_jar/apktool_2.5.0.jar")
        # 获取jvm.dll 的文件路径
        jvmpath = jpype.getDefaultJVMPath()
        # 开启jvm
        jpype.startJVM(jvmpath, "-ea", "-Djava.class.path={}:{}:{}:{}".format(jarpath,jarpath2,jarpath3,jarpath4))
        # 加载java类（参数是java的长类名）
        javaclass = jpype.JClass("Main")
        # 实例化java对象
        # javaInstance = javaClass()

        # 调用java方法，由于我写的是静态方法，直接使用类名就可以调用方法
        path = os.path.abspath(os.path.join(os.getcwd(), targetapk))
        print(path)
        launch_path = javaclass.getIndexurl(path)
        # 通过os.system也能执行，但是没有执行结果，只有执行成功与否的结果
        #launch_path = os.system("java -classpath /home/user/IdeaProjects/decodeAppcan/out/artifacts/decodeAppcan_jar/decodeAppcan.jar:/home/user/IdeaProjects/decodeAppcan/out/artifacts/decodeAppcan_jar/kxml2-2.3.0.jar:/home/user/IdeaProjects/decodeAppcan/out/artifacts/decodeAppcan_jar/xmlpull-1.1.3.1.jar Main /home/user/Downloads/appcan2.apk")
        print(launch_path)
        extract_folder = "null"
        #(str(prop))就将java.lang.string转换为python的str
        #如果起始页地址以"file:///android_asset/widget/"开头，则认为是hybrid开发，则需要提取apk相应目录下的文件。另外还要判断提取的文件是否加密，如果加密了则还需要解密。
        if (str(launch_path)).startswith("file:///android_asset/widget/"):
            extract_folder = self.extractFromHybridApp("working_folder")
            cipherkey = javaclass.getCipherkey()
            self.decrypt(extract_folder, cipherkey)

        return extract_folder, launch_path


def main():
    f = "../../../test_case/appcan_unencrypted.apk"
    appcan = Appcan(f, "android")
    if appcan.doSigCheck():
        logging.info("cordova signature Match")

    extract_folder, launch_path = appcan.doExtract(f)
    log.info("{} is extracted to {}, the start page is {}".format(f, extract_folder, launch_path))

    return

if __name__ == "__main__":
    sys.exit(main())
