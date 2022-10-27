# backend

## File structure
```
.
└── app
    ├── assets
    │   ├── robots
    │   │   ├── avatar      # {robot_id}.{png|jpg|jpeg}
    │   │   └── code        # {robot_id}.py
    │   └── users           # {username}.{png|jpg|jpeg}
    ├── core
    │   ├── models          # database entities
    │   │   └── tests       # database tests
    │   ├── schemas         # endpoint schemes
    │   └── settings.py     # database config
    ├── main.py             # main entrypoint
    └── views               # endpoint routers
        └── tests           # endpoint tests
```

## Quickstart
To initialize server, you should run:
```sh
   $> python -m venv venv
   $> source venv/bin/activate
   $> python -m pip install -r requirements.txt
   $> uvicorn app.main:app --reload
```
