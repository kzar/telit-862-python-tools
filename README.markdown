About
-----

This repository serves to group together a bunch of scripts I've been writing
to assist in the development process with the [Telit 862GPS](http://www.telit.com/en/products/gsm-gprs.php?p_ac=show&p=7). They are all designed for Linux.

I recommend also checking out [my blog post on the 862](http://kzar.co.uk/blog/view/embedded-development-setup-with-macbook) for some more details.

rs-send-python.py
-----------------

Useful script to send Python code to the Telit unit via GNU screen. Supports
uploading plain sourcecode and cross-compilation using TelitPy1.5.2+_v4.1.exe 
and Wine. (See the usage help and also header of the file for more details.)

telit-pyo.py
------------

Handy script designed to be run on the Telit unit itself. It dumps all pyo
files to serial in a friendly hex format that's easy to reconstruct.

decode-telit-pyo.py
-------------------

Lovely script that takes the output of telit-pyo.py and reconstructs all of
the pyo files. It checks the length against what was reported to highlight
problems.
