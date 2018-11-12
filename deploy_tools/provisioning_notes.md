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
  ```console
  server$ cat ./deploy_tools/nginx.template.conf \
      | sed "s/DOMAIN/staging.mysite.com/g" \
      | sed "s/USERNAME/myuser/g" \
      | sudo tee /etc/nginx/sites-available/staging.mysite.com
  ```
  (where the contents of the template get piped into sed, which replaces
  all instances of DOMAIN with staging.mysite.com and then pipes into
  tee which writes to the /etc/... file and stdout. We don't really care
  about directing the output to two places, but this is a way of elevating
  a non-root action to root for writing to a file.)
- symlink sites-enabled to sites-available
  ```console
  server$ sudo ln -s /etc/nginx/sites-available/staging.mysite.com \
      /etc/nginx/sites-enabled/staging.mysite.com
  ```


systemd Service
---------------

- see gunicorn-systemd.template.service
- replace DOMAIN with, e.g., staging.mysite.com:
- replace USERNAME with the appropriate Unix username
  ```console
  server$ cat ./deploy_tools/gunicorn-systemd.template.service \
      | sed "s/DOMAIN/staging.mysite.com/g" \
      | sed "s/USERNAME/myuser/g" \
      | sudo tee /etc/systemd/system/gunicorn-staging.mysite.com.service
  ```



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
