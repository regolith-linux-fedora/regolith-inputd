# Source1 is not in the repository. ext-rpm.sh makes it on the runner while it
# builds the SRPM, with `cargo vendor --locked` against Cargo.lock, so COPR
# builds offline from the SRPM.

Name:           regolith-inputd
Version:        0.4.1
Release:        1%{?dist}
Summary:        Daemon that applies GNOME input settings to sway
# regolith-inputd is Apache-2.0 (debian/copyright; its Cargo.toml names no
# license, the blank line in the summary). The rest covers the vendored
# crates: update it from the %%{cargo_license_summary} output in the build log
# whenever Cargo.lock changes.
License:        Apache-2.0 AND MIT AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND (Unlicense OR MIT)
URL:            https://github.com/regolith-linux/regolith-inputd
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  systemd-rpm-macros
# The gio and glib crates link against the system libraries.
BuildRequires:  pkgconfig(gio-2.0)

# The daemon reads the org.gnome.desktop.input-sources and
# org.gnome.desktop.peripherals.* schemas. The copies in the repository are
# not installed, as in Debian.
Requires:       gsettings-desktop-schemas
# Without a GSettings backend, changes made by the settings app never reach
# the daemon. Upstream added dconf-gsettings-backend to debian/control after
# the Baseline.
Requires:       dconf
# Debian recommends gnome-control-center; on Fedora Regolith's own settings
# app comes first.
Recommends:     (regolith-control-center or gnome-control-center)

%description
A daemon for the sway session that applies the keyboard layouts and the
keyboard and pointing device settings stored in GSettings to sway, so the
settings app works in a sway session, and copies changes made in sway back to
GSettings.

%prep
%autosetup -a1
%cargo_prep -v vendor

%build
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
# The crate has a library target (src/lib.rs), so %%cargo_install would also
# install its sources under %%{_datadir}/cargo/registry. Install the binary.
install -Dpm 0755 target/rpm/regolith-inputd %{buildroot}%{_bindir}/regolith-inputd
install -Dpm 0644 data/regolith-init-inputd.service %{buildroot}%{_userunitdir}/regolith-init-inputd.service
# Debian's postinst (dh_installsystemduser) runs `deb-systemd-helper --user
# enable regolith-init-inputd.service`, which links it into
# regolith-wayland.target.wants for every user. A user preset does the same
# through %%systemd_user_post.
install -d %{buildroot}%{_userpresetdir}
echo "enable regolith-init-inputd.service" > %{buildroot}%{_userpresetdir}/90-regolith-inputd.preset

%check
%cargo_test

%post
%systemd_user_post regolith-init-inputd.service

%preun
%systemd_user_preun regolith-init-inputd.service

%postun
%systemd_user_postun regolith-init-inputd.service

%files
%license LICENSE.dependencies cargo-vendor.txt
%{_bindir}/regolith-inputd
%{_userunitdir}/regolith-init-inputd.service
%{_userpresetdir}/90-regolith-inputd.preset

%changelog
* Tue Nov 10 2026 Regolith Fedora Port <port@regolith.invalid> - 0.4.1-1
- Initial package
