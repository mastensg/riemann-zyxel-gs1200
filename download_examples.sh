#!/bin/sh -eu

# Usage:
#
#   ./download_examples.sh http://10.13.37.240

BASE="${1}"

cd examples

for d in \
    igmp \
    LAG \
    link \
    loop \
    mirror \
    poe \
    port_state \
    qos \
    rate \
    system \
    VLAN_1Q_List
do
    file="${d}_data.js"
    url="${BASE}/${file}"

    rm -f "${file}"
    echo "${url}"
done | xargs -n 100 wget
