from fastapi import FastAPI
from datetime import datetime
app = FastAPI()
db = [
    {
        'id': 1,
        'name': "product 1",
        'price': 5.9,
        'image': "img.jpg"
    },
    {
        'id': 2,
        'name': "product 2",
        'price': 10.9,
        'image': "img1.jpg"
    },
    {
        'id': 3,
        'name': "product 4",
        'price': 9.9,
        'image': "img2.jpg"
    },
    {
        'id': 4,
        'name': "product 5",
        'price': 8.9,
        'image': "img3.jpg"
    },
    {
        'id': 5,
        'name': "product 6",
        'price': 5,
        'image': "img4.jpg"
    },
    {
        'id': 6,
        'name': "product 7",
        'price': 1,
        'image': "img4.jpg"
    },
    {
        'id': 7,
        'name': "product 8",
        'price': 9,
        'image': "img4.jpg"
    },
    {
        'id': 8,
        'name': "product 9",
        'price': 5.9,
        'image': "img1.jpg"
    },
    {
        'id': 9,
        'name': "product 10",
        'price': 6,
        'image': "img5.jpg"
    },
    {
        'id': 10,
        'name': "product 11",
        'price': 8,
        'image': "img3.jpg"
    },
    {
        'id': 11,
        'name': "product 12",
        'price': 4,
        'image': "img3.jpg"
    },
    {
        'id': 12,
        'name': "product 13",
        'price': 28,
        'image': "img5.jpg"
    },
    {
        'id': 13,
        'name': "product 14",
        'price': 10.9,
        'image': "img1.jpg"
    },
    {
        'id': 14,
        'name': "product 15",
        'price': 9.9,
        'image': "img3.jpg"
    },
    {
        'id': 15,
        'name': "product 16",
        'price': 8.9,
        'image': "img5.jpg"
    },
    {
        'id': 16,
        'name': "product 80",
        'price': 9.9,
        'image': "img2.jpg"
    },
    {
        'id': 17,
        'name': "product 15",
        'price': 8.9,
        'image': "img1.jpg"
    },
    {
        'id': 18,
        'name': "product 17",
        'price': 5,
        'image': "img4.jpg"
    }
]

@app.get('/')
def products():
    return db

@app.get('/customers')
def customs():
    return [
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        {'name':'Diqui Joaquim','adress':'djoaquimnamueto@gmail.com','contact':'+258860716912','orders':5,'status':'active'},
        
    ]

@app.get('/orders')
def get_orders():
    return [
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
        {'id':"27728",'date':datetime.now(),'amount':56,'cat':"food",'menu':"xima arroz"},
    ]
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)

#download the simple server api