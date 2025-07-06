#!/data/data/com.termux/files/usr/bin/bash

set -e

# Update and upgrade packages
pkg update -y && pkg upgrade -y

# Install required packages if not already installed
for pkgname in coreutils python gzip texinfo info util-linux; do
    if ! command -v "${pkgname%% *}" >/dev/null 2>&1; then
        pkg install -y "$pkgname"
    fi
done
python setup.py install --freedom=partial
echo "All required packages are installed ."