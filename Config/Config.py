import configparser
import os
import platform


if platform.system() == "Windows":
    cwd = os.getcwd().split("\\")
else:
    cwd = os.getcwd().split("/")

print("CWD", cwd)
print(cwd)
root_index = cwd.index("InstagramBot")
ROOT_PATH = "/".join(cwd[: root_index + 1])
config = configparser.ConfigParser()
config.read(ROOT_PATH + "/config.ini")
# config.read("/config.ini")


def GetConfig(service, key):
    try:
        return config[service][key]
    except Exception as e:
        print(e)
