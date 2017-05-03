#!/bin/bash
#
# Uses gem2rpm to build RPMs for requested packages.
# Will forego building spec from template if spec exists (allowing ad-hoc editting). 
# 

. ./deps.sh


RPMBUILDDIR=~jhover/rpmbuild
TEMPLATE=~/etc/rubygem-GEM.spec.template
PKGLOG=~/mkgem2rpm.pkg.log

#echo " " > $PKGLOG

for gem in $GEMS; do
    echo "Handling $gem ..."
    cd $RPMBUILDDIR/SOURCES
    gem fetch $gem
    echo "Matching..."
    ls $RPMBUILDDIR/SOURCES/$gem-[0-9]*.gem
    echo "Done"
    if ! [ -e "$RPMBUILDDIR/SPECS/rubygem-$gem.spec" ]; then 
       echo "$RPMBUILDDIR/SPECS/rubygem-$gem.spec does not exist. Creating from template..." 
            gem2rpm -t $TEMPLATE  $gem-[0-9]*.gem > $RPMBUILDDIR/SPECS/rubygem-$gem.spec
            ls -alh $RPMBUILDDIR/SPECS/rubygem-$gem.spec
    else
        echo "$RPMBUILDDIR/SPECS/rubygem-$gem.spec does exist. Skipping build"
    
    fi
    rpmbuild -bb $RPMBUILDDIR/SPECS/rubygem-$gem.spec
    if !  [ $? -eq 0 ]; then
        echo "*******************************************************"
        echo "$gem failed to build. *******************************************"
        echo "*******************************************************"
        echo "$gem build failed" >> $PKGLOG
        
        sleep 5
    else
        echo "$gem build succeeded" >> $PKGLOG
    fi

done


