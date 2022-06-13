# Dashboard-using-flask

Installation
Install with pip:

$ pip install -r requirements.txt
Flask Application Structure


Flask Configuration
Example
app = Flask(__name__)
app.config['DEBUG'] = True
Configuring From Files
Example Usage
app = Flask(__name__ )
cfg example

##Flask settings
DEBUG = True  # True/False
TESTING = False


....



Run Flask
Run flask for develop
$ python webapp/run.py
In flask, Default port is 5000

Swagger document page: http://127.0.0.1:5000/api

Run flask for production
** Run with gunicorn **

In webapp/

$ gunicorn -w 4 -b 127.0.0.1:5000 run:app

-w : number of worker
-b : Socket to bind

![image](https://user-images.githubusercontent.com/54638339/173277904-7b7f6e50-2aa5-41b8-8346-f6d8a101d513.png)
![image](https://user-images.githubusercontent.com/54638339/173277939-bff3cced-c734-49bb-abaa-b6b8f3a0d514.png)
![image](https://user-images.githubusercontent.com/54638339/173277993-4ca23f93-58f3-40ff-a919-f2db26f92f62.png)
![image](https://user-images.githubusercontent.com/54638339/173278035-b436debc-da86-4894-9ace-318722cfa513.png)
![image](https://user-images.githubusercontent.com/54638339/173279070-c4409b82-ca32-4b66-b31c-1dafef3f0b7f.png)

![image](https://user-images.githubusercontent.com/54638339/173278749-d871b5d8-bee0-4aba-9126-821e6fc95282.png)

