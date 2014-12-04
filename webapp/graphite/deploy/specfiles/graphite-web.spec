%define         my_app_name     graphite-web
%define         _description    SpilGames graphite-web patched

Summary:        ${_description}

Requires: python27-libs
BuildRequires: python27 python27-devel python27-distribute python-virtualenv

# Filled by DOS template engine
%define     my_app_ver      {{VER}}
%define     my_app_rel      {{SPI}}

%define     pip_index_url   http://pypi.shp/softengi/live

# set command used to create virtualenv
%define     virtualenv      /usr/bin/virtualenv --python=python2.7

%define     django_dbupdate 1
%define     django_db_args  --database=migration

# https://github.com/spilgames/specfiles/blob/master/templates/spil-libs-python-project-v3.inc
%include %{_topdir}/SOURCES/spil-libs-python-project-v3.inc
