#!/bin/sh

set -e

cd "$(dirname "$0")/.."

DATA_DIR=".data"

VERSION="3"
VERSION_FILE="$DATA_DIR/.version"

# Usage: exit_if_data_dir_is_up_to_date
function exit_if_data_dir_is_up_to_date() {

    # The data directory is up to date if the .version file exists and the version stored
    # in the .version file is newer than the version of the script that created it
    if [ -f "$VERSION_FILE" ]; then
        stored_version="$(cat "$VERSION_FILE")"
        if [ ! "$VERSION" -gt "$stored_version" ]; then
            echo "Data directory is up to date. Exiting..."
            exit 0
        fi
    fi
}

# Usage: create_version_file
function create_version_file() {
    echo "$VERSION" > "$VERSION_FILE"
}

exit_if_data_dir_is_up_to_date
rm -rf "$DATA_DIR"


TMP_DIR="$DATA_DIR/.tmp"

function get_certificate_path() {
    ca_dir="$1"
    echo "$ca_dir/certificate.pem"
}

function get_key_path() {
    ca_dir="$1"
    echo "$ca_dir/key.pem"
}

function get_csr_path() {
    ca_dir="$1"
    echo "$ca_dir/csr.pem"
}

function get_extfile_path() {
    ca_dir="$1"
    echo "$ca_dir/extfile.cnf"
}

# Usage: create_root_ca <organizationalUnit> <ca_dir>
function create_root_ca() {
    organizationalUnit="$1"

    ca_dir="$2"
    mkdir -p "$ca_dir"

    ca_key="$(get_key_path "$ca_dir")"
    ca_certificate="$(get_certificate_path "$ca_dir")"

    country="PT"
    locality="Porto"
    organization="ESS"

    openssl genrsa -out "$ca_key" 4096
    openssl req -new -x509 -days 3650 -key "$ca_key" -sha256 -batch -utf8 -out "$ca_certificate" -subj "/C=$country/L=$locality/O=$organization/OU=$organizationalUnit"
}

# Usage: create_sub_ca <organizationalUnit> <root_ca_dir> <ca_dir> [<extfile>]
function create_sub_ca_with_optional_extfile() {
    organizationalUnit="$1"

    root_ca_dir="$2"
    root_ca_key="$(get_key_path "$root_ca_dir")"
    root_ca_certificate="$(get_certificate_path "$root_ca_dir")"

    ca_dir="$3"
    mkdir -p "$ca_dir"

    ca_key="$(get_key_path "$ca_dir")"
    ca_csr="$(get_csr_path "$ca_dir")"
    ca_certificate="$(get_certificate_path "$ca_dir")"

    extfile="$4"
    
    extraOpts=""
    if [ -n "$extfile" ]; then
        extraOpts="-extfile $extfile"
    fi

    country="PT"
    locality="Porto"
    organization="ESS"

    openssl genrsa -out "$ca_key" 4096
    openssl req -sha256 -new -key "$ca_key" -out "$ca_csr" -subj "/C=$country/L=$locality/O=$organization/OU=$organizationalUnit"

    openssl x509 -req -days 365 -sha256 -in "$ca_csr" -CA "$root_ca_certificate" -CAkey "$root_ca_key" -out "$ca_certificate" -CAcreateserial $extraOpts
}

# Usage: create_sub_ca <organizationalUnit> <root_ca_dir> <ca_dir>
function create_sub_ca() {
    create_sub_ca_with_optional_extfile "$@"
}

# Usage: create_cert_with_dns <dns> <organizationalUnit> <root_ca_dir> <ca_dir>
function create_cert_with_dns() {
    dns="$1"
    organizationalUnit="$2"
    
    ca_dir="$4"
    mkdir -p "$ca_dir"
    
    ca_extfile="$(get_extfile_path "$ca_dir")"

    echo "basicConstraints=CA:FALSE" > "$ca_extfile"
    echo "subjectAltName = @alt_names" >> "$ca_extfile"
    echo "[alt_names]" >> "$ca_extfile"
    echo "DNS.1 = $dns" >> "$ca_extfile"

    shift 2
    create_sub_ca_with_optional_extfile "$organizationalUnit/CN=$dns" "$@" "$ca_extfile"
}

COMMUNICATIONS_CA_DIR="$TMP_DIR/communications_ca"
AUTHENTICATION_SERVER_CERT_DIR="$TMP_DIR/authentication_server_cert"
AUTHORIZATION_SERVER_CERT_DIR="$TMP_DIR/authorization_server_cert"
RESOURCE_SERVER_CERT_DIR="$TMP_DIR/resource_server_cert"
WEB_SERVER_CERT_DIR="$TMP_DIR/web_server_cert"

IDENTITY_CA_DIR="$TMP_DIR/identity_ca"
AUTHENTICATION_SERVER_IDENTITY_CA_DIR="$TMP_DIR/authentication_server_identity_ca"

create_root_ca "Communications Certification Authority" "$COMMUNICATIONS_CA_DIR"
create_cert_with_dns "authentication-server.local" "Authentication Server" "$COMMUNICATIONS_CA_DIR" "$AUTHENTICATION_SERVER_CERT_DIR"
create_cert_with_dns "authorization-server.local" "Authorization Server" "$COMMUNICATIONS_CA_DIR" "$AUTHORIZATION_SERVER_CERT_DIR"
create_cert_with_dns "resource-server.local" "Resource Server" "$COMMUNICATIONS_CA_DIR" "$RESOURCE_SERVER_CERT_DIR"
create_cert_with_dns "web-server.local" "Web Server" "$COMMUNICATIONS_CA_DIR" "$WEB_SERVER_CERT_DIR"

create_root_ca "Identity Certification Authority" "$IDENTITY_CA_DIR"
create_sub_ca "Authentication Server Identity Certification Authority" "$IDENTITY_CA_DIR" "$AUTHENTICATION_SERVER_IDENTITY_CA_DIR"

TMP_SERVER_DIR="$TMP_DIR/.server"

# Usage: create_data_directory <server_name>
function create_data_directory() {
    server_dir="$DATA_DIR/$1"
    mkdir -p "$server_dir/.."

    if [ -d "$TMP_SERVER_DIR" ]; then
        cp -r "$TMP_SERVER_DIR/." "$server_dir"
        rm -rf "$TMP_SERVER_DIR"
    fi
}

# Usage: copy_file_as <path> <new_name>
function copy_file_as() {
    TARGET_FILE="$TMP_SERVER_DIR/$2"
    mkdir -p "$(dirname "$TARGET_FILE")"

    cp -r "$1" "$TARGET_FILE"
}

# Usage: copy_own_certificate_and_key <cert_dir>
function copy_own_certificate_and_key() {
    cert_dir="$1"
    copy_file_as "$(get_certificate_path "$cert_dir")" "own_dns_certificate/certificate.pem"
    copy_file_as "$(get_key_path "$cert_dir")" "own_dns_certificate/key.pem"
}

# Usage: copy_dns_certificates
function copy_dns_certificates() {
    copy_file_as "$(get_certificate_path "$AUTHENTICATION_SERVER_CERT_DIR")" "dns_certificates/authentication_server.pem"
    copy_file_as "$(get_certificate_path "$AUTHORIZATION_SERVER_CERT_DIR")" "dns_certificates/authorization_server.pem"
    copy_file_as "$(get_certificate_path "$RESOURCE_SERVER_CERT_DIR")" "dns_certificates/resource_server.pem"
    copy_file_as "$(get_certificate_path "$WEB_SERVER_CERT_DIR")" "dns_certificates/web_server.pem"
}

# Usage: create_flask_directory
function create_flask_directory() {
    mkdir -p "$TMP_SERVER_DIR/flask_instance"
}

# Usage: copy_ca <ca_dir>
function copy_ca() {
    ca_dir="$1"
    copy_file_as "$ca_dir" "ca/"
}

# Usage: copy_communications_ca
function copy_communications_ca() {
    copy_file_as "$(get_certificate_path "$COMMUNICATIONS_CA_DIR")" "communications_ca/certificate.pem"
}

copy_own_certificate_and_key "$AUTHENTICATION_SERVER_CERT_DIR"
copy_dns_certificates
create_flask_directory
copy_communications_ca
copy_file_as "$(get_certificate_path "$AUTHENTICATION_SERVER_IDENTITY_CA_DIR")" "identity_ca/certificate.pem"
copy_file_as "$(get_key_path "$AUTHENTICATION_SERVER_IDENTITY_CA_DIR")" "identity_ca/key.pem"
create_data_directory "authentication_server"

copy_own_certificate_and_key "$AUTHORIZATION_SERVER_CERT_DIR"
copy_dns_certificates
create_flask_directory
copy_communications_ca
copy_file_as "$(get_certificate_path "$AUTHENTICATION_SERVER_IDENTITY_CA_DIR")" "identity_ca/certificate.pem"
create_data_directory "authorization_server"

copy_own_certificate_and_key "$RESOURCE_SERVER_CERT_DIR"
copy_dns_certificates
create_flask_directory
copy_communications_ca
create_data_directory "resource_server"

copy_own_certificate_and_key "$WEB_SERVER_CERT_DIR"
copy_dns_certificates
create_flask_directory
copy_communications_ca
create_data_directory "web_server"

copy_ca "$COMMUNICATIONS_CA_DIR"
create_data_directory "communications_ca"

copy_ca "$IDENTITY_CA_DIR"
create_data_directory "identity_ca"

create_data_directory "mailpit"

rm -rf "$TMP_DIR"


# Usage: fix_file_permissions
function fix_file_permissions() {
    find "$DATA_DIR" -type f -name '*.pem' -exec chmod 444 {} \;
    find "$DATA_DIR" -type f -name '*.srl' -exec chmod 666 {} \;
    find "$DATA_DIR" -type d -exec chmod 777 {} \;
}

fix_file_permissions


# Create the .version file, so that the data directory is not recreated, if not needed
create_version_file
