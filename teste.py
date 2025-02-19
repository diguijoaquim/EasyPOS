from requests import post,get

res=get('http://127.0.0.1:8000/orders').text
print(res)