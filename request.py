import requests

#URL FOR CAR 1
url = 'http://20.20.10.188:5000/received'
#MESSAGE
msg = {'msg':'Lat: 8.94398 Long: 125.52312'}

#POST REQUEST TO SERVER
requests.post(url,data=msg)

