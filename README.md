# Local Flask forward proxy

Local flask based forward proxy webapp. The flask app acts as a forward proxy allowing you to look into whatever data gets passed to a website working with upto http 1.1 .


Improvements need to be made for http2 based connections

run the application with

`python local_flask_proxy_all.py`

then access some url in your browser lets say you visit pagamesssddr

`localhost:5000/pagamesssddr.com/login`

you should see the login details captured in `data_logs.txt`

For this reason it is important that you use a trustable proxy service if you use one at all
