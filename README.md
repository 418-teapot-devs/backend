# backend

## File structure
```
.
└── src
   ├── core
   │   ├── models		# database entities
   │   ├── schemas		# endpoint schemes
   │   └── settings.py		# database configuration
   ├── main.py			# main entry point
   └── views			# endpoit routers
```

## Quickstart
To initialize server, you should run:
```sh
   $> python -m venv venv
   $> source venv/bin/activate
   $> pip install -r requirements
   $> uvicorn main:app --app-dir src --reload
```
