import requests

host = "http://192.168.1.160:5000"
rutaapi = "/api"

uid_str = "FF,FF,FF,FF"
print "Card read UID: ", uid_str
r = requests.get(host + rutaapi + str("/") + uid_str)  # , auth=('user', 'pass')
if r.status_code != 200:
    print "algo fallo, status code: ", r.status_code
    quit(1)

print "respuesta: ", r.content