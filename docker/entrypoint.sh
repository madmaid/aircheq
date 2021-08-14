#!/bin/sh

set -Ceux
# echo "HOST_UID: $HOST_UID, HOST_GID: $HOST_GID"
# cat /etc/passwd
# cat /etc/group

USERNAME=aircheq
CONFIG_DIR=/home/aircheq/.aircheq/

if ! cat /etc/passwd | grep "$USERNAME"; then
    useradd --system --create-home --shell /sbin/nologin "$USERNAME"
    # : 'useradd --system --create-home --shell /sbin/nologin "$USERNAME"'
fi

if [ "`id --user \"$USERNAME\"`" != "$HOST_UID" ]; then
    usermod --uid "$HOST_UID" --non-unique "$USERNAME"
    # : 'usermod --uid "$HOST_UID" --non-unique "$USERNAME"'
fi

# ユーザーがホストの GID と同じグループに所属していないなら、所属させる
if ! id --groups "$USERNAME" | tr ' ' '\n' | grep -x "$HOST_GID"; then
    usermod --gid "$HOST_GID" "$USERNAME"
    # : 'groupmod --gid "$HOST_GID" "$USERNAME"'
fi

if [ ! -d "$CONFIG_DIR" ]; then
    mkdir -p "$CONFIG_DIR"
    # : 'mkdir -p "$CONFIG_DIR"'
fi
exec "$@"
# set +x
