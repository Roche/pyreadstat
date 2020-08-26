libname samples '/home/bceuser/fajardoo/pyreadstat_samples';

FILENAME REFFILE '/home/bceuser/fajardoo/pyreadstat_samples/sample.csv';
        
PROC IMPORT DATAFILE=REFFILE
			DBMS=CSV REPLACE
			OUT=SAMPLES.sample;
			GETNAMES=YES;
RUN;