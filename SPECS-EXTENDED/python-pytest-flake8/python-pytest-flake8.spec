Vendor:         Microsoft Corporation
Distribution:   Azure Linux
# Created by pyp2rpm-3.3.2
%global pypi_name pytest_flake8
%global pkg_name pytest-flake8

Name:           python-%{pkg_name}
Version:        1.3.0
Release:        1%{?dist}
Summary:        pytest plugin to check FLAKE8 requirements
Group:          Development/Python
License:        BSD License
URL:            https://pypi.org/project/pytest-flake8/
Source0:        https://files.pythonhosted.org/packages/source/p/%{pypi_name}/%{pypi_name}-%{version}.tar.gz
BuildArch:      noarch
 
BuildRequires:  python3-devel
BuildRequires:  python3dist(flake8) >= 3.5
BuildRequires:  python3dist(pytest) >= 3.5
BuildRequires:  python3dist(setuptools)
BuildRequires:  python3-setuptools_scm
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-pluggy
BuildRequires:  python-pytest-runner
BuildRequires:  python3-importlib-metadata

%description
pytest plugin for efficiently checking PEP8 compliance.

%package -n     python3-%{pkg_name}
Summary:        %{summary}
%{?python_provide:%python_provide python3-%{pkg_name}}

%description -n python3-%{pkg_name}
pytest plugin for efficiently checking PEP8 compliance.


%prep
%autosetup -n %{pypi_name}-%{version}
rm -rf %{pypi_name}.egg-info

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files pytest_flake8

%check
%pytest

%files -n python3-%{pkg_name} -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Fri Oct 15 2021 Pawel Winogrodzki <pawelwi@microsoft.com> - 1.0.4-6
- Initial CBL-Mariner import from Fedora 32 (license: MIT).

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.4-4
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.4-3
- Rebuilt for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Apr 04 2019 Dan Radez <dradez@redhat.com> - 1.0.4-1
- update to 1.0.4

* Wed Feb 27 2019 Miro Hrončok <mhroncok@redhat.com> - 1.0.1-3
- Subpackage python2-pytest-flake8 has been removed
  See https://fedoraproject.org/wiki/Changes/Mass_Python_2_Package_Removal

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Jul 11 2018 Neal Gompa <ngompa13@gmail.com> - 1.0.1-1
- Initial package
