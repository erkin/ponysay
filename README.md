# Ponysay in Kuroko

This is a port of [ponysay](https://github.com/erkin/ponysay) to [Kuroko](https://kuroko-lang.github.io/).

Kuroko is a dialect of Python with explicit variable declaration and block scoping. Kuroko's standard library is incomplete and not fully compatible with Python, so this port needed to work around various issues.

This repository has been stripped of some extraneous files to make it more suitable for use a submodule in [PonyOS](https://github.com/klange/ponyos), so some files specific to, eg., Linux console usage, as well as build and packaging scripts for the Python version have been removed.

