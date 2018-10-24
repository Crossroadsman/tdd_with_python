from selenium import webdriver

"""To enable firefox to run on a headless Ubuntu server we need to:
- install firefox
- install xvfb (the X windows virtual framebuffer)
- Run xvfb in the background
```console
Xvfb :10 -ac &
```
- set the DISPLAY variable
```console
export DISPLAY=:10
```
"""
browser = webdriver.Firefox()
browser.get('http://localhost:8000')

assert 'Django' in browser.title
