proc format library=HOME.missing_formats;
value A
  .A = "missing";
run ;

Options fmtsearch=(work HOME.missing_formats);

proc formats library=HOME.missing_formats cntlout=mjh;
run;

data HOME.missing_test;
  format var1 A.;
  var1=.A;
  var2=.B;
  var3=.C;
  var4=.X;
  var5=.Y;
  var6=.Z;
  var7=._;
  var8=.;
  var9=1;
  
run;

