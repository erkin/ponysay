# Maintainer: jaseg <arch@jaseg.net>

pkgname=ponysay-jaseg-git
pkgver=0.984.85fffca
pkgrel=1
pkgdesc="Cowsay. With ponies. Improved, faster, 20% cooler fork."
arch=('any')
license=('GPL')
url="https://github.com/jaseg/ponysay"
depends=('python')
makedepends=('git' 'pixelterm')
provides=('ponysay')
source=('git+https://github.com/jaseg/ponysay#branch=master')
md5sums=('SKIP')

_gitname="ponysay"

pkgver() {
  cd "$srcdir/$_gitname"
  microver="$(git log -1 --pretty=format:%h )"
  minorver="$(git rev-list --count HEAD)"
  echo "0.$minorver.$microver"
}

build() {
  cd "${srcdir}/$_gitname"
  make
}

package() {
  cd "${srcdir}/$_gitname"
  python setup.py install --root="$pkgdir"
}
