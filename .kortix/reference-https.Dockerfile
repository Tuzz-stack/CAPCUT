# Local reference transport prelude; fixed e56 adds its complete runtime after this file.
FROM ubuntu@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac
WORKDIR /workspace
RUN set -eu \
    && test "$(dpkg --print-architecture)" = amd64 \
    && printf '%s\n' '9a4af756e974a7a6b0a447705d1d12366cfa4d860d8722b652d69d8e1b44e34f  /etc/apt/sources.list.d/ubuntu.sources' | sha256sum -c - \
    && printf '%s\n' '80a36b0a6de2f69f49d2df75ef473ccde121e9e190b9ea01d20a4f63778d5c31  /usr/share/keyrings/ubuntu-archive-keyring.gpg' | sha256sum -c - \
    && printf '%s\n' '8ce6407d5487bed332b5fcb4aab26dacf3f516d811c26792efb0c67f06f1958b  /etc/apt/sources.list' | sha256sum -c - \
    && test "$(find /etc/apt/sources.list.d -maxdepth 1 -type f)" = /etc/apt/sources.list.d/ubuntu.sources \
    && cp /etc/apt/sources.list.d/ubuntu.sources /tmp/kortix-reference-original.sources \
    && sed 's/^Components: main universe restricted multiverse$/Components: main/' /tmp/kortix-reference-original.sources > /etc/apt/sources.list.d/ubuntu.sources \
    && printf '%s\n' '5e9a607f38ec5d67ae182dd902796b2cac7769afa1e3b9f122b0cc47622f24e6  /etc/apt/sources.list.d/ubuntu.sources' | sha256sum -c - \
    && printf '%s\n' 'Acquire::Retries "0";' 'Acquire::http::Timeout "10";' 'Acquire::https::Timeout "10";' 'Acquire::http::Dl-Limit "512";' 'Acquire::https::Dl-Limit "512";' 'Acquire::http::AllowRedirect "false";' 'Acquire::https::AllowRedirect "false";' 'Acquire::http::Proxy "DIRECT";' 'Acquire::https::Proxy "DIRECT";' 'Acquire::https::Verify-Peer "true";' 'Acquire::https::Verify-Host "true";' 'Acquire::Check-Date "true";' 'Acquire::Check-Valid-Until "true";' 'Acquire::AllowInsecureRepositories "false";' 'Acquire::AllowDowngradeToInsecureRepositories "false";' 'APT::Get::AllowUnauthenticated "false";' 'Debug::Acquire::gpgv "true";' > /tmp/kortix-reference-apt.conf \
    && apt-get -c /tmp/kortix-reference-apt.conf update --error-on=any \
    && apt-get -c /tmp/kortix-reference-apt.conf --simulate --no-remove --no-install-recommends install ca-certificates \
    && apt-get -c /tmp/kortix-reference-apt.conf --print-uris --yes --no-remove --no-install-recommends install ca-certificates \
    && DEBIAN_FRONTEND=noninteractive apt-get -c /tmp/kortix-reference-apt.conf install --yes --no-remove --no-install-recommends ca-certificates \
    && test -s /etc/ssl/certs/ca-certificates.crt \
    && printf '%s\n' '5e9a607f38ec5d67ae182dd902796b2cac7769afa1e3b9f122b0cc47622f24e6  /etc/apt/sources.list.d/ubuntu.sources' | sha256sum -c - \
    && sed -e 's|^URIs: http://archive.ubuntu.com/ubuntu/$|URIs: https://archive.ubuntu.com/ubuntu/|' -e 's|^URIs: http://security.ubuntu.com/ubuntu/$|URIs: https://security.ubuntu.com/ubuntu/|' /tmp/kortix-reference-original.sources > /etc/apt/sources.list.d/ubuntu.sources \
    && printf '%s\n' '92d2ff28918561a6c5e4ebf241769a57b13eebd1504d77d7a3a77a73e368c5ec  /etc/apt/sources.list.d/ubuntu.sources' | sha256sum -c - \
    && mkdir -p /tmp/kortix-reference-https-lists/partial \
    && chown _apt:root /tmp/kortix-reference-https-lists/partial \
    && apt-get -c /tmp/kortix-reference-apt.conf -o Dir::State::Lists=/tmp/kortix-reference-https-lists update --error-on=any \
    && dpkg-query -W -f='${Package} ${Version}\n' ca-certificates openssl \
    && sha256sum /etc/ssl/certs/ca-certificates.crt \
    && rm -rf /tmp/kortix-reference-https-lists /tmp/kortix-reference-original.sources /tmp/kortix-reference-apt.conf
