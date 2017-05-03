#!/bin/bash
# 
# Rebuild all RPMs for rubygems

for specfile in `ls ~/rpmbuild/SPECS/rubygem-*.spec` ; do
        echo $specfile
        rpmbuild -bb $specfile
done
