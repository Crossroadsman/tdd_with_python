Provisioning a New Site
=======================

Required Packages
-----------------

- nginx
- Python (>=3.6)
- Venv (python3-venv)
- Pip (?) (venv will install pip in the venv, need to determine if we need
           it globally)
- Git
- (venv) Django (>=2.0)
- (venv) Gunicorn


Nginx Virtual Host Config
-------------------------

- see nginx.template.conf
- replace DOMAIN with, e.g., staging.mysite.com
- replace USERNAME with the approriate Unix username


systemd Service
---------------

- see gunicorn-systemd.template.service
- replace DOMAIN with, e.g., staging.mysite.com
- replace USERNAME with the appropriate Unix username


Folder Structure
----------------
Assume we have a user account at /home/username

/home/username
└── sites
    ├── DOMAIN1
    │    ├── .env
    │    ├── db.sqlite3
    │    ├── manage.py etc
    │    ├── static
    │    └── venv
    └── DOMAIN2
         ├── .env
         ├── db.sqlite3
         ├── etc...
