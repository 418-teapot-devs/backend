# backend

## File structure
```
.
├── app
│   ├── assets
│   │   ├── robots
│   │   │  ├── avatars # {robot_id}.{png|jpg|jpeg}
│   │   │  └── code    # {robot_id}.py
│   │   └── users      # {username}.{png|jpg|jpeg}
│   ├── game           # core game logic
│   ├── main.py        # main entrypoint
│   ├── models         # database entities
│   ├── schemas        # endpoint schemes
│   ├── util           # common utilities
│   └── views          # endpoint routers
└── tests
    ├── assets
    ├── game
    ├── models
    └── views
```

## Quickstart
To initialize server, you should run:
```sh
   $> python -m venv venv
   $> source venv/bin/activate
   $> python -m pip install -r requirements.txt
   $> python -m run         # run app
   $> python -m run tests   # run tests
```
