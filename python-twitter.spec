%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:           python-twitter
Version:        1.1
Release:        1%{?dist}
Summary:        Python Interface for Twitter API

Group:          Development/Libraries
License:        Apache License 2.0
URL:            http://github.com/bear/python-twitter
Source0:        http://python-twitter.googlecode.com/files/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:      noarch
Requires:       python >= 2.4, python-simplejson >= 2.0.7
BuildRequires:  python-setuptools


%description
This library provides a pure python interface for the Twitter API.


%prep
%setup -q


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
chmod a-x README
%{__python} setup.py install --skip-build --root $RPM_BUILD_ROOT


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc PKG-INFO README CHANGES COPYING LICENSE doc/twitter.html
# For noarch packages: sitelib
%{python_sitelib}/*


%changelog
* Sat Mar 22 2008 Steve 'Ashcrow' Milner <me@stevemilner.org> - 0.5-1
- Initial package.
