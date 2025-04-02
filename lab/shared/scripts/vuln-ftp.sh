#!/bin/bash

apt update -y

apt install -y vsftpd

cp /etc/vsftpd.conf /etc/vsftpd.conf.bak

cat <<EOL > /etc/vsftpd.conf
listen=YES
force_dot_files=YES
anon_umask=000
anonymous_enable=YES
write_enable=YES
local_enable=YES
anon_upload_enable=YES
anon_other_write_enable=YES
anon_mkdir_write_enable=YES
chroot_local_user=NO
chmod_enable=YES
allow_writeable_chroot=YES
ssl_enable=NO
anon_root=/var/ftp
EOL

mkdir -p /var/ftp/upload
chmod 555 /var/ftp
chmod 777 /var/ftp/upload
chown ftp:ftp /var/ftp/upload

systemctl restart vsftpd
systemctl enable vsftpd