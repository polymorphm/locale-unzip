locale-unzip
============

``locale-unzip`` is utility for unzip files with non-standard encoding of names.


Status
------

Release: locale-unzip-0.2.1 .


Usage Examples
--------------

Extract files from ``мой_архив.zip`` to ``каталог_для_распаковки``:

    /path/to/utility/cyrillic-unzip -d каталог_для_распаковки мой_архив.zip

Same operation, but using custom encoding:

    /path/to/utility/locale-unzip -d каталог_для_распаковки cp866 мой_архив.zip
