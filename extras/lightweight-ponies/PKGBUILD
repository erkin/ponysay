pkgname=lightweight-ponies
pkgver=2
pkgrel=1
pkgdesc="Featurefree lightweight ponysay script"
url="https://github.com/erkin/ponysay/extras/lightweight-ponies"
license=('custom:GNUAllPermissive')
arch=('any')
depends=('sh' 'grep' 'sed' 'findutils' 'coreutils' 'ponysay')
_commit=c4fc895c451838a78b93ede7f1ab1b63fdb5a4b9
source=("https://github.com/erkin/ponysay/archive/${_commit}.tar.gz")
sha256sums=('24ee8698f32d5b986efd36aab04f32420ffe57d501ec1594d992bc05555db546')

package() {
    cd "${srcdir}/ponysay-${_commit}/extras/lightweight-ponies"
    install -Dm755 -- lightweight-ponies "${pkgdir}/usr/bin/lightweight-ponies"
}

