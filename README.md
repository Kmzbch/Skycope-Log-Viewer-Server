# Skycope Log Viewer Server

This is a back-end solution project to the mini-project tech assessment of Skycope Technologies.

### How to run

#### 1. create a virtual

```
$ virtualenv venv
$ ./venv/Scripts/activate
```

#### 2. install dependencies

```
$(venv) pip install -r requirements
```

#### 3. run services


```
# run on another terminal
$(venv) python services/service1.py
```

```
# run on the other terminal
$(venv) python services/service2.py
```

#### 4. run the main script

```
$(venv) python main.py
```

### What are covered
#### Covered
- Python 3
    - Flask
- TypeScript
    - Angular12
- HTML 5
- Bootstrap
- CSS3/SASS/SCSS
- RESTful API

#### Not covered

- NGINX
- Deloployment on cloud(e.g. AWS)
- Multiprocessing for running services in backend process
