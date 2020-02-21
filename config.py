import configparser
import os


default_path = os.getcwd()
print(default_path)
default_path = default_path.replace("\\","/")
print(default_path)
cfg = configparser.ConfigParser()

cfg.read('mb2elo.cfg')



if cfg['SETTINGS']['port'] == "PORT":
    port = 29070
else:
    port = int(cfg['SETTINGS']['port'])


if cfg['SETTINGS']['ip'] == "IP":
    ip = "127.0.0.1"
else:
    ip = cfg['SETTINGS']['ip']


if cfg['SETTINGS']['logname'] == "LOGNAME":
    logname = default_path + "/MBII/server.log"
else:
    logname = default_path + "/MBII/" + cfg['SETTINGS']['logname']


if cfg['SETTINGS']['elogain'] == "ELOGAIN":
    elogain = 10
else:
    elogain = int(cfg['SETTINGS']['elogain'])


print(port,ip,logname,elogain)