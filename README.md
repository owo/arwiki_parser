## About
**arwiki_parser** is a small python script for extracting plain text articles from
Arabic Wikipedia dumps.


## Requirements:
The scripts should run on any unix-like system with **Python 2.7** installed along with
**pip** or **easy_install** to install additional packages.

The following third-party libraries neead to be installed as well:
 
 - Beautiful Soup 4: `$ pip install beautifulsoup4`
 - mwlib: `$ pip install mwlib mwlib.xhtml`
 - lxml: `$ pip install lxml`


## Usage:
```
$ python arwiki_parser.py path/to/dump.xml path/to/output/dir/
```

The script will extract each article into separate files. To make dealing with 
the files easier on a window manager, the files are distributed across 256 
directories with hexadecimal names *00-ff*. All articles are stored as
*&lt;article_id&gt;.txt*. The first line in each file is always the title of the
article.


## License:
arwiki_parser -  Extract plain text from Arabic Wikipedia dumps.
Copyright (C) 2014  Ossama W. Obeid

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
