Summary:        The SymCrypt engine for OpenSSL (SCOSSL) allows the use of OpenSSL with SymCrypt as the provider for core cryptographic operations
Name:           SymCrypt-OpenSSL
Version:        1.6.1
Release:        1%{?dist}
License:        MIT
Vendor:         Microsoft Corporation
Distribution:   Azure Linux
Group:          System/Libraries
URL:            https://github.com/microsoft/SymCrypt-OpenSSL
Source0:        https://github.com/microsoft/SymCrypt-OpenSSL/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
BuildRequires:  openssl-devel
BuildRequires:  SymCrypt >= 103.6.0
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make

Requires:       SymCrypt >= 103.6.0
Requires:       openssl

%description
The SymCrypt engine for OpenSSL (SCOSSL) allows the use of OpenSSL with SymCrypt as the provider for core cryptographic operations

# Only x86_64 and aarch64 are currently supported
%ifarch x86_64
%define symcrypt_arch AMD64
%endif

%ifarch aarch64
%define symcrypt_arch ARM64
%endif

%prep
%setup -q

%build
mkdir bin; cd bin

cmake   .. \
        -DOPENSSL_ROOT_DIR="%{_prefix}/local/ssl" \
        -DSYMCRYPT_ROOT_DIR=%{buildroot}%{_includedir}/.. \
        -DCMAKE_TOOLCHAIN_FILE="../cmake-toolchain/LinuxUserMode-%{symcrypt_arch}.cmake" \
        -DCMAKE_BUILD_TYPE=RelWithDebInfo

cmake --build .

%install
mkdir -p %{buildroot}%{_libdir}/engines-3/
mkdir -p %{buildroot}%{_libdir}/ossl-modules/
mkdir -p %{buildroot}%{_includedir}
mkdir -p %{buildroot}%{_sysconfdir}/pki/tls/

# We still install the engine for backwards compatibility with legacy applications. Callers must
# explicitly load the engine to use it. It will be removed in a future release.
install bin/SymCryptEngine/dynamic/symcryptengine.so %{buildroot}%{_libdir}/engines-3/symcryptengine.so
install bin/SymCryptProvider/symcryptprovider.so %{buildroot}%{_libdir}/ossl-modules/symcryptprovider.so
install SymCryptEngine/inc/e_scossl.h %{buildroot}%{_includedir}/e_scossl.h
install SymCryptProvider/symcrypt_prov.cnf %{buildroot}%{_sysconfdir}/pki/tls/symcrypt_prov.cnf

%check
./bin/SslPlay/SslPlay

%files
%license LICENSE
%{_libdir}/engines-3/symcryptengine.so
%{_libdir}/ossl-modules/symcryptprovider.so
%{_includedir}/e_scossl.h
%{_sysconfdir}/pki/tls/symcrypt_prov.cnf

%changelog
* Wed Nov 27 2024 CBL-Mariner Servicing Account <cblmargh@microsoft.com> - 1.6.1-1
- Auto-upgrade to 1.6.1 - bug fixes

* Mon Nov 25 2024 Tobias Brick <tobiasb@microsoft.com> - 1.6.0-1
- Upgrade to SymCrypt-OpenSSL 1.6.0

* Wed Oct 02 2024 Tobias Brick <tobiasb@microsoft.com> - 1.5.1-2
- Add sources to debuginfo package

* Wed Aug 21 2024 Maxwell Moyer-McKee <mamckee@microsoft.com> - 1.5.1-1
- Fix minor behavior differences with default provider

* Thu Aug 15 2024 Maxwell Moyer-McKee <mamckee@microsoft.com> - 1.5.0-1
- Fix AES-CFB to match expected OpenSSL calling patterns
- Support ECC key X and Y coordinate export

* Thu May 16 2024 Maxwell Moyer-McKee <mamckee@microsoft.com> - 1.4.3-1
- Additional bugfixes for TLS connections
- Add variable length GCM IV support to the SymCrypt engine

* Thu Apr 25 2024 Maxwell Moyer-McKee <mamckee@microsoft.com> - 1.4.2-1
- Support additional parameters in the SymCrypt provider required for TLS connections
- Various bugfixes for TLS scenarios

* Wed Apr 17 2024 Maxwell Moyer-McKee <mamckee@microsoft.com> - 1.4.1-1
- Update SymCrypt-OpenSSL to v1.4.1
- Adds support for RSASSA-PSS keys, SP800-108 KDF
- Fixes smoke test for check in OpenSSL 3.1

* Thu Dec 28 2023 Maxwell Moyer-McKee <mamckee@microsoft.com> - 1.4.0-1
- Update SymCrypt-OpenSSL to v1.4.0.
- Adds SymCrypt-OpenSSL provider for OpenSSL 3.

* Mon May 22 2023 Samuel Lee <saml@microsoft.com> - 1.3.0-1
- Update SymCrypt-OpenSSL to v1.3.0. Adds support for HMAC and fixes corner RSA-PSS bug. Run smoke test in check

* Mon Jun 06 2022 Samuel Lee <saml@microsoft.com> - 1.2.0-1
- Update SymCrypt-OpenSSL to v1.2.0 to improve performance and fix some corner case bugs

* Tue Mar 29 2022 Samuel Lee <saml@microsoft.com> - 1.1.0-1
- Update SymCrypt-OpenSSL to v1.1.0 to include FIPS self-tests, and fix aarch64 build

* Mon Feb 14 2022 Samuel Lee <saml@microsoft.com> - 1.0.0-1
- Original version for CBL-Mariner
- Verified license
