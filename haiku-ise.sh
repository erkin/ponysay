#!sh
sed -i 's_#!/usr/bin/env python3_#!python_g' *.py
sed -i 's_print(_printout(_g' *.py
sed -i 's_.buffer._._g' *.py
sed -i 's_\x1b39_\x1b37_g' */*.pony
sed -i 's_\x1b49_\x1b40_g' */*.pony
sed -i 's_;39_;37_g' */*.pony
sed -i 's_;49_;40_g' */*.pony
sed -i 's_sys.std_std_g' *.py
sed -i 's_def printout(_stdout = os.fdopen(1, '\''wb'\'')\x0adef printout(_g' *.py
sed -i 's_def printerr(_stderr = os.fdopen(2, '\''wb'\'')\x0adef printerr(_g' *.py
sed -i 's_stdout = _stdin = os.fdopen(0, '\''rb'\'')\x0astdout = _g' *.py
