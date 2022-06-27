Name:             mksh
Version:          59.3
Release:          1
Summary:          MirBSD enhanced version of the Korn Shell
License:          MirOS and ISC and BSD
URL:              https://www.mirbsd.org/mksh.htm
Source0:          https://www.mirbsd.org/MirOS/dist/mir/%{name}/%{name}-R59c.tgz
Source1:          dot-mkshrc
Source2:          rtchecks.expected

BuildRequires:    gcc util-linux ed
Requires(post):   grep
Requires(postun): sed
Provides:         lksh mksh
Conflicts:        filesystem < 3

%description
mksh is the MirBSD Korn Shell, an actively developed free implementation of the Korn Shell programming language
and a successor to the Public Domain Korn Shell (pdksh). It is developed as part of the MirOS Project as
native Bourne/POSIX/Korn shell for MirOS BSD, but also to be readily available under other UNIX-like operating systems.
It targets users who desire a compact, fast, reliable, secure shell not cut off modern extensions, with unicode support.

%package          help
Summary:          Help documents for mksh

%description      help
The mksh-help package conatins manual pages and other related files for mksh.

%prep
%autosetup -n %{name} -p1

cat >rtchecks <<'EOF'
typeset -i sari=0
typeset -Ui uari=0
typeset -i x=0
print -r -- $((x++)):$sari=$uari. #0
let --sari --uari
print -r -- $((x++)):$sari=$uari. #1
sari=2147483647 uari=2147483647
print -r -- $((x++)):$sari=$uari. #2
let ++sari ++uari
print -r -- $((x++)):$sari=$uari. #3
let --sari --uari
let 'sari *= 2' 'uari *= 2'
let ++sari ++uari
print -r -- $((x++)):$sari=$uari. #4
let ++sari ++uari
print -r -- $((x++)):$sari=$uari. #5
sari=-2147483648 uari=-2147483648
print -r -- $((x++)):$sari=$uari. #6
let --sari --uari
print -r -- $((x++)):$sari=$uari. #7
(( sari = -5 >> 1 ))
((# uari = -5 >> 1 ))
print -r -- $((x++)):$sari=$uari. #8
(( sari = -2 ))
((# uari = sari ))
print -r -- $((x++)):$sari=$uari. #9
EOF

%build
CFLAGS="$RPM_OPT_FLAGS -DMKSH_DISABLE_EXPERIMENTAL" LDFLAGS="$RPM_LD_FLAGS" sh Build.sh -r
cp test.sh test_mksh.sh
export HAVE_PERSISTENT_HISTORY=0
CFLAGS="$RPM_OPT_FLAGS -DMKSH_DISABLE_EXPERIMENTAL" LDFLAGS="$RPM_LD_FLAGS" sh Build.sh -L -r
cp -f test.sh test_lksh.sh

%install
install -D -m 755 mksh $RPM_BUILD_ROOT%{_bindir}/mksh
install -D -m 755 lksh $RPM_BUILD_ROOT%{_bindir}/lksh
install -D -m 644 mksh.1 $RPM_BUILD_ROOT%{_mandir}/man1/mksh.1
install -D -m 644 lksh.1 $RPM_BUILD_ROOT%{_mandir}/man1/lksh.1
install -D -p -m 644 dot.mkshrc $RPM_BUILD_ROOT%{_sysconfdir}/mkshrc
install -D -p -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/skel/.mkshrc

%check
./mksh rtchecks >rtchecks.got 2>&1
if ! cmp --quiet rtchecks.got %{SOURCE2}
then
  echo "rtchecks failed"
  diff -Naurp %{SOURCE2} rtchecks.got
  exit 1
fi

for tf in test_mksh.sh test_lksh.sh
do
  echo > test.wait
  script -qc "./$tf"' -v; x=$?; rm -f test.wait; exit $x'
  maxwait=0
  while test -e test.wait; do
    sleep 1
    maxwait=$(expr $maxwait + 1)
    test $maxwait -lt 900 || break
  done
done

%post
grep -q "^/bin/mksh$" %{_sysconfdir}/shells 2>/dev/null || \
  echo "/bin/mksh" >> %{_sysconfdir}/shells
grep -q "^%{_bindir}/mksh$" %{_sysconfdir}/shells 2>/dev/null || \
  echo "%{_bindir}/mksh" >> %{_sysconfdir}/shells

%postun
if [ ! -x %{_bindir}/mksh ]; then
  sed -e 's@^/bin/mksh$@POSTUNREMOVE@' -e '/^POSTUNREMOVE$/d' -i %{_sysconfdir}/shells
  sed -e 's@^%{_bindir}/mksh$@POSTUNREMOVE@' -e '/^POSTUNREMOVE$/d' -i %{_sysconfdir}/shells
fi

%files
%doc dot.mkshrc
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/mkshrc
%config(noreplace) %{_sysconfdir}/skel/.mkshrc

%files help
%{_mandir}/man1/*

%changelog
* Sat Jun 11 2022 YukariChiba <i@0x7f.cc> - 59.3-1
- Upgrade version

* Tue Jan 18 2022 SimpleUpdate Robot <tc@openeuler.org> - 59-1
- Upgrade to version 59

* Wed Nov 20 2019 liujing<liujing144@huawei.com> - 56c-5
- Package init
