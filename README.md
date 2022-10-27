# backend

## File structure
```
.
└── app
   ├── assets
   │  ├── robots
   │  │  ├── avatar  # {robot_id}.{png|jpg|jpeg}
   │  │  └── code    # {robot_id}.py
   │  └── users      # {username}.{png|jpg|jpeg}
   ├── game          # core game logic
   ├── models        # database entities
   │  └── tests      # database tests
   ├── schemas       # endpoint schemes
   ├── views         # endpoint routers
   │  └── tests      # endpoint tests
   └── main.py       # main entrypoint
```

## Quickstart
To initialize server, you should run:
```sh
   $> python -m venv venv
   $> source venv/bin/activate
   $> python -m pip install -r requirements.txt
   $> uvicorn app.main:app --reload
```
