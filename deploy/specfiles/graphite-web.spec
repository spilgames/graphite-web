%define         my_app_name     spil-libs-graphite-web
%define         _description    Spil Custom build of graphite web which supports threading

Summary:        ${_description}

Requires: python uwsgi mysql
BuildRequires: python27 python27-devel python27-distribute python-virtualenv
BuildRequires: mysql mysql-devel openssl-devel openssl-devel
BuildRequires: git unzip cairo-devel sqlite-devel libevent-devel

# Filled by DOS template engine
%define     my_app_ver      {{VER}}
%define     my_app_rel      {{SPI}}
%define     my_app_prefix

%define     pip_index_url   http://pypi.shp/softengi/live

# set command used to create virtualenv
%define     virtualenv      /usr/bin/virtualenv --python=python2.7

%define     django_dbupdate 0

# https://github.com/spilgames/specfiles/blob/master/templates/spil-libs-python-project-v3.inc
%include %{_topdir}/SOURCES/spil-libs-python-project-v3.inc
