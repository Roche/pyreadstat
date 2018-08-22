libname basic '/home/bceuser/fajardoo/PyCharm_Projects/pyreadstat/test_data/basic';

FILENAME REFFILE '/home/bceuser/fajardoo/PyCharm_Projects/pyreadstat/test_data/basic/dates.csv';
        
PROC IMPORT DATAFILE=REFFILE
			DBMS=CSV REPLACE
			OUT=basic.dates;
			GETNAMES=YES;

RUN;