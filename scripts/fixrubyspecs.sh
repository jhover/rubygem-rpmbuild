#!/bin/bash
#
# Fix for RHEL/FEDORA 
#
#  Replace 
#     %define gemdir /usr/share/rubygems
#  with
#     %define gemdir /usr/share/gems
#
#


for specfile in `ls ~/rpmbuild/SPECS/rubygem-*.spec` ; do
        echo $specfile
        grep -rl "%define gemdir /usr/share/rubygems" \
        $specfile | \
        xargs sed -i -e 's|%define gemdir /usr/share/rubygems|%define gemdir /usr/share/gems|'
done
