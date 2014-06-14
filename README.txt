About:
======
arwiki_parser is a small python script for extracting plain text articles from
Arabic Wikipedia dumps.


Requirements:
=============
The scripts should run on any unix system with Python 2.7 installed along with
pip to install additional packages.

The following third-party libraries neead to be installed as well:

    - Beautiful Soup 4:
          pip install beautifulsoup4

    - mwlib:
	  pip install mwlib mwlib.xhtml

    - lxml:
          pip install lxml


Usage:
======
$ python arwiki_parser.py path/to/dump.xml path/to/output/dir/

The script will extract each article into separate files. To make dealing with 
the files easier on a window manager, the files are distributed across 256 
directories with hexadecimal names 00-FF. All articles are stored as
<article_id>.txt. The first line in each file is always the title of the
article.


License:
========
This software is licensed under GNU General Public License, version 3 (GPL-3.0).
(http://www.gnu.org/licenses/gpl-3.0.txt)

Copyright 2014 Ossama W. Obeid
