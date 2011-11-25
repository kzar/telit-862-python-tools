About
-----

This repository serves to group together a bunch of scripts I've been writing
to assist in the development process with the [Telit 862GPS](http://www.telit.com/en/products/gsm-gprs.php?p_ac=show&p=7). They are all designed for Linux with the exception of the bulkdownload script which is for Windows.

I recommend also checking out [my blog post on the 862](http://kzar.co.uk/blog/view/embedded-development-setup-with-macbook) for some more details.

telit-send-python.py
-----------------

Useful script to send Python code to the Telit unit via GNU screen. Supports
uploading plain sourcecode and cross-compilation using TelitPy1.5.2+_v4.1.exe 
and Wine. Handles files above 7kb and (if patch below) is applied produces
identical .pyo's to the unit itself.

Allows for a nice workflow as you can type commands into the GNU Screen session
and then, without closing things, send files using this script. Just requires
Python, GNU Screen and optionally Wine + Telit Python so it's easy to get running on
most systems.

(See the usage help and also header of the file for more details.)

telit-pyo.py
------------

Handy script designed to be run on the Telit unit itself. It dumps all pyo
files to serial in a friendly hex format that's easy to reconstruct.

decode-telit-pyo.py
-------------------

Lovely script that takes the output of telit-pyo.py and reconstructs all of
the pyo files. It checks the length against what was reported to highlight
problems.

telit862-python-crosscompile-fix.patch
--------------------------------------

Patch for the /Python/Lib/py-compile.py cross compiling script contained in TelitPy v4.1.
Not vital but it replaces the timestamp with FF's as the Telit unit itself does, I only
noticed the difference when I was troubleshooting a problem transmitting binary files
accross the serial line.

repl.py
-------

Python REPL (evaluate Python interactively) for the Telit module. Handy for testing things
although it's power is limited by the eval() function's limitations.

bulkdownload
------------

Script to automate Python transfer if you're using the standard Telit tools on a windows machine.

 - Put bulkdownload.py in C:\Program Files\Python\Lib
 - Put bulkdownload.bat in a directory containing pyo or py files
 - Click the batch file to have all the py files in the same directory compiled to pyo and
   then all the pyo files downloaded