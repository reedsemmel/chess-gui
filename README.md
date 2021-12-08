# Chess

This is a program for playing chess using a GUI written in Python and PyQt5.
This program was created by Alishan Bhayani, Chris Degawa, and Reed Semmel
for CS340 Software Engineering at UTK.

### How to use

Download the repository. Install Python 3 if you do not have it. You will also
need to install the `PyQt5` and `stockfish` packages. You can install them with
the following command:

```bash
pip install --user PyQt5
pip install --user stockfish
```

Note that depending on your system, the command may be `pip` or `pip3` for
Python 3. Refer to your system's manual. Tested to run with Python 3.8

### Installing stockfish

You **must** also install the actual engine. Stockfish works by creating a
CLI interface that a GUI program interacts with. The `stockfish` package is
just a python wrapper around this binary. You must install the actual engine
to your PATH and make it executable. If you do not, you must specify the file
path in the settings each time you launch the application.

To download or compile Stockfish, visit their [downloads page](https://stockfishchess.org/download/) or their [GitHub](https://github.com/official-stockfish/Stockfish).

To run the program:

```bash
python src/app_main.py
```

from the root of the repository, though it should work from any relative path.

### Licensing

This program is licensed under the GPL v3 only. View the README in assets for
licensing of non-code assets.
