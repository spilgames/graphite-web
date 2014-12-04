# Copy this file one directory up, and fill in the settings below

%define         my_app_name     graphite-web
%define         _description    Spil Custom build of graphite web

Summary:        ${_description}

# Filled by DOS template engine
%define	    my_app_ver      {{VER}}
%define     my_app_rel      {{SPI}}

Name:       %{my_app_name}

# Define default values
%define     my_app_arch     x86_64
%define	    my_app_py		/opt/graphite
%define	    my_app_venv		/opt/virtualenv
%define     pip_index_url   http://pypi.shp/softengi/live

Group:      Applications/Internet
Version:    %{my_app_ver}
Release:    %{my_app_rel}%{?dist}
BuildArch:  %{my_app_arch}

License:    Proprietary
Source0:    %{my_app_name}-%{my_app_ver}.tar.gz
Source1:    %{_topdir}/SOURCES/spil-libs-python-project.inc
BuildRoot:  %{_tmppath}/%{name}-%{my_app_ver}-%{my_app_rel}-root-%(%{__id_u} -n )

BuildRequires: python-setuptools python-virtualenv python-devel git unzip cairo-devel sqlite-devel libevent-devel mysql mysql-devel openssl-devel
Requires: python uwsgi mysql

%description
%{_description}

%prep
rm -rf $RPM_BUILD_DIR/*
rm -rf ${RPM_BUILD_ROOT}
%setup -n %{my_app_name}-%{my_app_ver} -q
rm -f setup.cfg

%install
install -d -m 0750 ${RPM_BUILD_ROOT}%{my_app_py}

# add version file
mkdir -p DOC
echo %{my_app_ver} > DOC/VERSION

## Create virtualenv environment
mkdir -p ${RPM_BUILD_ROOT}%{my_app_venv}
virtualenv --no-site-packages ${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}
export PATH=$PATH:${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}/bin

pip_success=false
# install requirements, first use mirrors to speed up download, also use build cache, this action may fail
${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}/bin/pip --verbose install --use-mirrors --no-index -r requirements.txt --build /tmp/dos_cache/pip_build_cache && pip_success=true || true

if [ $pip_success == false ];then
  # install requirements from main index, this may fail
  ${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}/bin/pip --verbose install -r requirements.txt  --build /tmp/dos_cache/pip_build_cache  && pip_success=true || true
fi

# if using cache failed, do failsafe
if [ $pip_success == false ];then
  # remove cache and uncompleted virtualenv
  rm -R /tmp/dos_cache/pip_build_cache/* ${RPM_BUILD_ROOT}%{my_app_venv} || true

  # create everything new
  mkdir -p ${RPM_BUILD_ROOT}%{my_app_venv}
  virtualenv --no-site-packages ${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}

  # install requirements from main index, fallback, this may not fail
  ${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}/bin/pip --verbose install -r requirements.txt --build /tmp/dos_cache/pip_build_cache
fi

# Install application inside our virtualenv
mkdir -p ${RPM_BUILD_ROOT}%{my_app_py}/webapp
${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}/bin/python setup.py install --prefix=${RPM_BUILD_ROOT}%{my_app_py} --install-lib=${RPM_BUILD_ROOT}%{my_app_py}/webapp

# strip all shared libraries from debug symbols containing buildroot
find /tmp/dos_cache ${RPM_BUILD_ROOT} -name '*.so' -exec strip {} \;
find /tmp/dos_cache ${RPM_BUILD_ROOT} -name '*.o' -exec strip {} \;

# remove all references to buildroot from other files
find /tmp/dos_cache ${RPM_BUILD_ROOT} -type f -exec sed -i "s|${RPM_BUILD_ROOT}||g" {} \;

# fix lib64 symlink
ln -sfT %{my_app_venv}/%{my_app_name}/lib ${RPM_BUILD_ROOT}%{my_app_venv}/%{my_app_name}/lib64

# Install uwsgi config files
if [ `ls DOC/uwsgi/*.ini` ];then
	%{__install} -d ${RPM_BUILD_ROOT}/etc/uwsgi/
	%{__install} DOC/uwsgi/*.ini ${RPM_BUILD_ROOT}/etc/uwsgi/
fi

# Install supervisord files
if [ `ls DOC/supervisord/*.ini` ];then
	%{__install} -d ${RPM_BUILD_ROOT}/etc/supervisord.d/
	%{__install} DOC/supervisord/*.ini ${RPM_BUILD_ROOT}/etc/supervisord.d/
fi

# Install nginx files
if [ `ls DOC/nginx/*.ngx` ];then
	%{__install} -d ${RPM_BUILD_ROOT}/etc/nginx/vhosts/
	%{__install} DOC/nginx/*.ngx ${RPM_BUILD_ROOT}/etc/nginx/vhosts/
fi

# Install cron files
if [ `ls DOC/cron.d/*.cron` ];then
	%{__install} -d ${RPM_BUILD_ROOT}/etc/cron.d/
	%{__install} DOC/cron.d/*.cron ${RPM_BUILD_ROOT}/etc/cron.d/
fi

# generate file list for etc files
find ${RPM_BUILD_ROOT}/etc -type f | sed "s|${RPM_BUILD_ROOT}||g" > files.txt

# Create log directory
%{__install} -d ${RPM_BUILD_ROOT}/bigdisk/logs/python/%{my_app_name}/
%{__install} -d ${RPM_BUILD_ROOT}/bigdisk/logs/uwsgi/

%files -f files.txt
%defattr(0644,root,uwsgi,2750)
%{my_app_py}/

%defattr(-,root,root,-)
%{my_app_venv}/%{my_app_name}/

%clean
rm -rf $RPM_BUILD_DIR/*
rm -rf ${RPM_BUILD_ROOT}

%post
# start newly added uwsgi config files
/sbin/service uwsgi start
# reload already existing config file
/sbin/service uwsgi reload

# reload nginx
/sbin/service nginx reload

# reload supervisord
/sbin/service supervisord reload

%postun
# when removing package
if [ "$1" = "0" ]; then
	#stop nginx vhosts which are removed
	/sbin/service nginx reload
fi

%changelog

# The following files will be installed from the source:
# DOC/uwsgi/* -> /etc/uwsgi/
# DOC/nginx/* -> /etc/nginx/vhosts/
# DOC/supervisord/* -> /etc/supervisord.d/
# DOC/cron.d/* -> /etc/cron.d/
# README.md -> /bigdisk/docs/LIBS/${my_app_name}/
# DOC/* -> /bigdisk/docs/LIBS/%{my_app_name}/DOC/
# INC/* -> /bigdisk/docs/INC/%{my_app_name}/
# WEBROOT/* -> /bigdisk/docs/WEBROOT/%{my_app_name}/

# Version will be written to file /bigdisk/docs/LIBS/%{my_app_name}/DOC/VERSION

# The specfile will install the setup.py script from the project source root into the virtualenv /opt/virtualenv/%{my_app_name}/
