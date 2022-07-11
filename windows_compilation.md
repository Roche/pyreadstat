# Compiling pyreadstat on windows

## Context

Python extensions can be compiled in two ways: using Microsoft Visual Studio with a version matching that of your 
python (see [here](https://blogs.msdn.microsoft.com/pythonengineering/2016/04/11/unable-to-find-vcvarsall-bat/),
 and [here](https://wiki.python.org/moin/WindowsCompilers)), or using MinGW, which is a mini-linux environment to 
cross-compile for windows, but using all the linux compiling toolchain.
Since Python 3.5, the recommended way is using Visual Studio, as Microsoft introduced changes in the compiler that are 
not 100% compatible with MINGW, actually it is recommended not to use mingw 
(see [this](https://stevedower.id.au/blog/building-for-python-3-5/) and [this](https://github.com/cython/cython/wiki/CythonExtensionsOnWindows)). 
In the past, Readstat (the library that pyreadstat wraps) was written in a way that depended on Posix (unix) libraries, 
and therefore could not be compiled with Visual Studio, therefore, one must compile with MINGW. 
In more recent revisions of Readstat, it is now possible to compile with Microsoft Visual Studio, and therefore this is now 
the recommended way. I keep here also at the end how to compile with mingw with two different ways as it was done before

## Using Microsoft Visual Studio Compiler

This assumes that MSVC is installed and working. The only pre-requisite before compiling is that we need two external libraries
compiled with the same MSVC version as we pretend to compile pyreadstat, and the static libraries and header files should be copied
to the win\_libs/64bit folder in pyreadstat:

```
# libiconv
git clone https://github.com/kiyolee/libiconv-win-build.git
msbuild.exe libiconv-win-build/build-VS2019-MT/libiconv.sln /property:Configuration=Release;Platform=X64
copy libiconv-win-build\\include\\iconv.h pyreadstat\\win_libs\\64bit                                   
copy libiconv-win-build\\build-VS2019-MT\\x64\\Release\\libiconv-static.lib  pyreadstat\\win_libs\\64bit
# libz
git clone https://github.com/kiyolee/zlib-win-build.git
msbuild.exe zlib-win-build/build-VS2019-MT/zlib.sln /property:Configuration=Release;Platform=X64
copy zlib-win-build\\zlib.h pyreadstat\\win_libs\\64bit                                   
copy zlib-win-build\\zconf.h pyreadstat\\win_libs\\64bit                                   
copy zlib-win-build\\build-VS2019-MT\\x64\\Release\\libz-static.lib  pyreadstat\\win_libs\\64bit
``` 

Maybe you observed that win\_libs/64 bit already contains the files needed. It may be therefore that those already
works for you, but chances are that MSVC is going to compile that those files were not generated with the same
MSVC version as you have, and therefore you have to do what is descrived before.

Once this is done, one can build the library as usual:
```
python setup.py build_ext --inplace
```

Of course any other variant of installation (setup.py install, pip etc) should work as well. 


## Using m2w64-toolchain

Initially I compiled using purely Msys2/MingW64. This approach however requires lot of manual tweaking (see later) and is not
compatible with CI services such as appveyor. Now I am using m2w64-toolchain which is a conda package that makes the
process much easier and is compatible with Appveyor.

pre-requisite:

* Install Anaconda or Miniconda and prepare the environment: run these commands on the Anaconda prompt and/or activate the conda 
environment properly

```
conda install setuptools pandas wheel pip libpython cython
conda install -c msys2 m2w64-toolchain
```

* compilation:

```
# set mingw32 as compiler
python setup.py config --compiler=mingw32
# Create a wheel. 
python setup.py bdist_wheel 
# install the wheel
pip install --pre --no-index --find-links dist/ pyreadstat
# run tests (optional)
python.exe tests\test_basic.py
```


## Using only Msys2/MingW64 (old)

Current Python versions do not support compiling with MingW64 out of the box anymore. Since it is not the recommended way,
there are going to be unexpected errors, which solution are not always evident (at least by googling it). Here a recipe that
did work for me in the past for several months until I changed the process to use m2w64-toolchain. There is no guarantee
tough that this will continue to work in the future.

1.	First we need to install MinGW. In the Readstat page, in the [windows specific notes](https://github.com/WizardMac/ReadStat#windows-specific-notes) 
says we should download it from [here](http://www.msys2.org/), we do and follow the instructions (basically install and
 then update with pacman –Syu or pacman –Syuu many times until it says there is nothing else to be updated. The first
  time the window has to be closed manually. For the following times, you can just repeat the command in the same window.
2.	Now, again in the msys command line window, we need to install the needed libraries for readstat to compile. From 
the readstat page:

```pacman -S autoconf automake libtool mingw-w64-x86_64-toolchain mingw-w64-x86_64-cmake mingw-w64-x86_64-libiconv```

All of this is needed in case you would like to compile Readstat binaries, but for us, 
theoretically we do not need everything, but just these:

```pacman -S mingw-w64-x86_64-toolchain mingw-w64-x86_64-libiconv```

3.	Now, from windows program list you can open MINGWX64 shell (not the msys anymore), navigate to whererever you put the 
pyreadstat source (for example: cd /c/workspace/repos/pyreadstat) and compile as usual, being careful to point at the 
right python path, for example:

```/c/ProgramData/Anaconda3/python setup.py build_ext –inplace```

I said theoretically because most likely at this point you will get problems, which introduces us to our next section.


## The problems (and their solutions)

As previously described, let’s say that on Mingw64, we navigate to the folder where pyreadstat source is and we do 
something like:

```/c/ProgramData/Anaconda3/python setup.py build_ext –inplace```

I got the following errors, in this order. I am assuming after each error correction you run again the above command, 
which introduces you into the next error.

1.	You get an error like this:
```
src\readstat.h(353): fatal error C1003: error count exceeds 100; stopping compilation
error: command 'C:\\Program Files (x86)\\Microsoft Visual Studio 14.0\\VC\\BIN\\x86_amd64\\cl.exe' failed with exit status 2
```

**What does it mean:** Python is trying to compile with Visual Studio, we have to instruct it to compile with mingw.

**Solution:** create a file distutils.cfg and put it into your python installation under Lib/distutils. In the file write the following:

```
[build]
compiler=mingw32
```

2.	After trying again, the next error is like this:

```
C:/msys64/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/7.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: cannot find -lmsvcr140
collect2.exe: error: ld returned 1 exit status
error: command 'C:\\msys64\\mingw64\\bin\\gcc.exe' failed with exit status 1
```

**what does it mean:** windows does not have the file msvcr140.dll anymore, but now uses vcruntime140.dll

**What to do:** in the folder distutils there is a file cygwincompiler.py. There are some lines like this in line number
 85 or so: [source](https://groups.google.com/a/continuum.io/forum/#!topic/anaconda/yLH46ilPQeo)
 
 ```

        elif int(msc_ver) >= 1900:
            # VS2015 / MSVC 14.0
            return ['msvcr140']

we will change it to this:

        ### PATCH###############################
        # INCLUDES NEWEST mscvcr VERSION
        #########################################
        elif msc_ver == '1900':
           # Visual Studio 2015 / Visual C++ 14.0
           # "msvcr140.dll no longer exists" http://blogs.msdn.com/b/vcblog/archive/2014/06/03/visual-studio-14-ctp.aspx
           return ['vcruntime140']
        #########################################
 ```

3.	The next error is like this:
```
C:/msys64/mingw64/bin/../lib/gcc/x86_64-w64-mingw32/7.3.0/../../../../x86_64-w64-mingw32/bin/ld.exe: cannot find -lvcruntime140
collect2.exe: error: ld returned 1 exit status
error: command 'C:\\msys64\\mingw64\\bin\\gcc.exe' failed with exit status 1
```

**what it means:** MingW cannot find vcruntime140.dll for some reason.

**What to do:**
 
 -	We need to figure out where is mingw looking for dlls. For that, in mingw do:
```
gcc -print-search-dirs
```
It will print three long lines, install, program and libraries. We are interested in libraries, so choose one of those 
paths (I choosed C:\msys64\mingw64\x86_64-w64-mingw32\lib).
 - In the Anaconda installation dir (C:\ProgramData\Anaconda3), there is a file vcruntime140.dll. Copy the file and 
paste it into the mingw directory we said before.

Notes:
-	Maybe there is cleaner way to instruct mingw to use the dll from Anaconda, I just could not find it in a reasonable 
    time, but there is information in the [mingw wiki](http://www.mingw.org/wiki/LibraryPathHOWTO)
-	Another possibility which I have not explored is to [rebuild  mingw pointing to the correct dll](https://www.spiria.com/en/blog/desktop-software/building-mingw-w64-toolchain-links-specific-visual-studio-runtime-library).
The main motivation for doing that is that they say ming is built against a different runtime dll as python and this 
can cause problems later. However, in my hands
mingw could not find the runtime, which probably means once we provide the same dll python is using we are fine (?)

4.	At this point things should work! At the least the compilation. Installation and create the wheel will also work. 
Build_ext inplace will work, but it wont be possible to import the library because two dlls may be missing, you could
 add them directly to the folder where you compiled, see additional notes.

## Additional notes:

### Old process (msys only)

1.	Iconv had to be added to setup.py to the list of needed libraries to compile the extensions. This was not needed on
 linux but on windows is necessary.
2.	On windows, it was necessary to add zlib1.dll and libiconv-2.dll to the [package](https://docs.python.org/3/distutils/setupscript.html).
 Those dlls I got from the mingw bin directory (C:\msys64\mingw64\bin), and now are in the win_libs directory. If you
 compile usig build_ext --inplace and then
  copy paste the dlls next to the pyd files, you will be able to import pyreadstat.
3.	When trying to import the library, if the error dll cannot be found appears, the program [dependency walker](http://www.dependencywalker.com/)
will help discovering which one is missing. Simply run the program, load the pyd file and it will show you. Many windows
 ones cannot be resolved, but those are typically in the Anaconda installation, so those should not be problematic.

### New process (m2w64-toolchain)

1. Dependency Walker does not work well anymore on Windows 10. Use [this one](https://github.com/lucasg/Dependencies) instead.
A very handy program is also [ListDlls](https://docs.microsoft.com/en-us/sysinternals/downloads/listdlls) that will list all dlls loaded by a 
process. This one however will not work if the dll is missing, so it helps only locating good loaded dlls.
2. During the update to the new process I also added compilation for 32 bit. zlib1.dll and libiconv-2.dll I got from the conda packages
zlib and iconv. The compilation introduces also a dependency to two extra dlls coming from the m2w64-toolchain, zlib and iconv also
depend on them so they have to be added. Interestingly this dependency does not exists for 64 bit.

