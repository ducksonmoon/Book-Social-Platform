# Some-Book-API
Hahaha
It's just another API for Nebig book.
> V1

## Commands
This handy guide will help you run projects and read documents:

1. Clone the project.
`````````
> git clone https://github.com/M-b850/Some-Book-API.git
> cd Some-Book-API/
`````````

> Ensure Python3 and Pip are correctly installed and functioning before proceeding to step 2.
> <br>
> Install virtualenv by running ``` pip3 install virtualenv ```

2. Create virtualend and install requirements.
`````````
> virtualenv venv
> source venv/bin/activate
> pip install -r requirements.txt
`````````

3. Make migrations and create database.
`````````
> ./manage.py makemigrations
> ./mange.py migrate
`````````

4. Run server.
````````
> ./manage.py runserver
````````
> Django runs its server on port `8000` by default. 
> You can run server on specific ports if you add port number after runserver command<br>
> example on port 9000: ``` ./manage.py runserver 9000 ``` <br>


## Help

You can find Documentations here:
`````
localhost:port/swagger/
`````
> example:
> `` http://127.0.0.1:8000/swagger/ ``

## TODO:
1. User [  ]
2. Book [  ] 
