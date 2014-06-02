#
%define nginx_home %{_localstatedir}/cache/nginx
%define nginx_user nginx
%define nginx_group nginx
%define libressl fbbc857

Summary: nginx-ssl is a high performance web server linked with uncrippled SSL
Name: nginx-ssl
Version: 1.7.1
Release: 1%{?dist}.ngx
Vendor: nginx inc.
URL: http://nginx.org/

Source0: http://nginx.org/download/nginx-%{version}.tar.gz
Source1: logrotate
Source2: nginx.init
Source3: nginx.sysconf
Source4: nginx.conf
#Build script for SOURCE5
#git clone https://github.com/busterb/libressl.git
#git checkout fbbc8570
#cd libressl
#./autogen.sh
#tar zcvf libressl-fbbc8570.tar.gz libressl/
Source5: libressl-%{libressl}.tar.gz
#Source6 from https://github.com/technion/mod_randpad/archive/v1.1.tar.gz
Source6: mod_randpad-1.1.tar.gz
Source7: nginx-libressl.patch


License: 2-clause BSD-like license
Group: System Environment/Daemons

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: perl
Requires: initscripts >= 8.36
Requires(pre): shadow-utils
Requires(post): chkconfig
Provides: webserver

%description
nginx [engine x] is an HTTP and reverse proxy server, as well as
a mail proxy server

%package debug
Summary: debug version of nginx
Group: System Environment/Daemons
Requires: nginx
%description debug
not stripped version of nginx build with the debugging log support

%prep
tar zxf %{SOURCE6}
tar zxf %{SOURCE5}
cd libressl
./configure
cd ..
%setup -q -n nginx-%{version}

%build
./configure \
        --prefix=%{_sysconfdir}/nginx \
        --sbin-path=%{_sbindir}/nginx \
        --conf-path=%{_sysconfdir}/nginx/nginx.conf \
        --error-log-path=%{_localstatedir}/log/nginx/error.log \
        --http-log-path=%{_localstatedir}/log/nginx/access.log \
        --pid-path=%{_localstatedir}/run/nginx.pid \
        --lock-path=%{_localstatedir}/run/nginx.lock \
        --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp \
        --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp \
        --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp \
        --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp \
        --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp \
        --user=%{nginx_user} \
        --group=%{nginx_group} \
        --with-http_ssl_module \
        --with-http_spdy_module \
        --with-openssl=../libressl \
        --with-http_realip_module \
        --with-file-aio \
        --with-ipv6 \
        --with-debug \
        --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
        --with-ld-opt="-Wl,-z,now -Wl,-z,rlo" \
        --add-module=../mod_randpad-1.1 \
        $*
patch -p1 <  %{SOURCE7}
make -j1
 
%{__mv} %{_builddir}/nginx-%{version}/objs/nginx \
        %{_builddir}/nginx-%{version}/objs/nginx.debug
./configure \
        --prefix=%{_sysconfdir}/nginx \
        --sbin-path=%{_sbindir}/nginx \
        --conf-path=%{_sysconfdir}/nginx/nginx.conf \
        --error-log-path=%{_localstatedir}/log/nginx/error.log \
        --http-log-path=%{_localstatedir}/log/nginx/access.log \
        --pid-path=%{_localstatedir}/run/nginx.pid \
        --lock-path=%{_localstatedir}/run/nginx.lock \
        --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp \
        --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp \
        --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp \
        --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp \
        --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp \
        --user=%{nginx_user} \
        --group=%{nginx_group} \
        --with-http_ssl_module \
        --with-http_spdy_module \
        --with-openssl=../libressl \
        --with-http_realip_module \
        --with-file-aio \
        --with-ipv6 \
        --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
        --with-ld-opt="-Wl,-z,now -Wl,-z,rlo" \
        --add-module=../mod_randpad-1.1 \
        $*
patch -p1 <  %{SOURCE7}
make -j1

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT install

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/nginx
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/html $RPM_BUILD_ROOT%{_datadir}/nginx/

%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/nginx/*.default
%{__rm} -f $RPM_BUILD_ROOT%{_sysconfdir}/nginx/fastcgi.conf

%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/run/nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/cache/nginx

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
%{__install} -m 644 -p %{SOURCE4} \
   $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
%{__install} -m 644 -p %{SOURCE3} \
   $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/nginx

# install SYSV init stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_initrddir}
%{__install} -m755 %{SOURCE2} \
   $RPM_BUILD_ROOT%{_initrddir}/nginx

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%{__install} -m 644 -p %{SOURCE1} \
   $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/nginx
%{__install} -m644 %{_builddir}/nginx-%{version}/objs/nginx.debug \
   $RPM_BUILD_ROOT%{_sbindir}/nginx.debug

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%{_sbindir}/nginx

%dir %{_sysconfdir}/nginx
%dir %{_sysconfdir}/nginx/conf.d

%config(noreplace) %{_sysconfdir}/nginx/nginx.conf
%config(noreplace) %{_sysconfdir}/nginx/mime.types
%config(noreplace) %{_sysconfdir}/nginx/fastcgi_params
%config(noreplace) %{_sysconfdir}/nginx/scgi_params
%config(noreplace) %{_sysconfdir}/nginx/uwsgi_params
%config(noreplace) %{_sysconfdir}/nginx/koi-utf
%config(noreplace) %{_sysconfdir}/nginx/koi-win
%config(noreplace) %{_sysconfdir}/nginx/win-utf

%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%config(noreplace) %{_sysconfdir}/sysconfig/nginx
%{_initrddir}/nginx

%dir %{_datadir}/nginx
%dir %{_datadir}/nginx/html
%{_datadir}/nginx/html/*

%attr(0755,root,root) %dir %{_localstatedir}/cache/nginx
%attr(0755,root,root) %dir %{_localstatedir}/log/nginx

%files debug
%attr(0755,root,root) %{_sbindir}/nginx.debug

%pre
# Add the "nginx" user
getent group %{nginx_group} >/dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} >/dev/null || \
    useradd -r -g %{nginx_group} -s /sbin/nologin \
    -d %{nginx_home} -c "nginx user"  %{nginx_user}
exit 0

%post
# Register the nginx service
if [ $1 -eq 1 ]; then
    /sbin/chkconfig --add nginx
    # print site info
    cat <<BANNER
----------------------------------------------------------------------

Thanks for using NGINX!

Check out our community web site:
* http://nginx.org/en/support.html

If you have questions about commercial support for NGINX please visit:
* http://www.nginx.com/support.html

----------------------------------------------------------------------
BANNER

    # Touch and set permisions on default log files on installation

    if [ -d %{_localstatedir}/log/nginx ]; then
        if [ ! -e %{_localstatedir}/log/nginx/access.log ]; then
            touch %{_localstatedir}/log/nginx/access.log
            %{__chmod} 640 %{_localstatedir}/log/nginx/access.log
            %{__chown} nginx:adm %{_localstatedir}/log/nginx/access.log
        fi

        if [ ! -e %{_localstatedir}/log/nginx/error.log ]; then
            touch %{_localstatedir}/log/nginx/error.log
            %{__chmod} 640 %{_localstatedir}/log/nginx/error.log
            %{__chown} nginx:adm %{_localstatedir}/log/nginx/error.log
        fi
    fi
fi

%preun
if [ $1 -eq 0 ]; then
    /sbin/service nginx stop > /dev/null 2>&1
    /sbin/chkconfig --del nginx
fi

%postun
if [ $1 -ge 1 ]; then
    /sbin/service nginx upgrade &>/dev/null || :
fi

%changelog
* Mon Jun 02 2014 Joshua Small <technion@lolware.net> 1.7.1-1
- Implemented LibreSSL
- Bump to nginx 1.7.1
* Mon Sep 16 2013 Joshua Small <technion@lolware.net> 1.5.4-2
- Included mod_randpad
* Sun Sep 08 2013 Joshua Small <technion@lolware.net> 1.5.4-1
- Initial release
