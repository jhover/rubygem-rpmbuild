#!/bin/env python
__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.0"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import argparse
import logging
import os
import subprocess
import sys
import time
from ConfigParser import ConfigParser

def _runtimedcommand(cmd):
    '''
    @param string:   Command shell string to be run. Can contain semicolons for compound commands. 
    
    '''
    log = logging.getLogger()
    before = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = None
    (out, err) = p.communicate()
    delta = time.time() - before
    log.debug('%s seconds to perform command' %delta)
    if p.returncode == 0:
        log.debug('Leaving with OK return code. Err is "%s"' % err)
    else:
        log.warning('Leaving with bad return code. rc=%s err=%s out=%s' %(p.returncode, err, out ))
        out = None
    return (out, err)


class GemBuildException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class GemHandler(object):
    
    handledgems = set()
    problemgems = set()
    
    def __init__(self, cp , gemname, skipdeps=False):
        self.log = logging.getLogger()
        self.log.info("Handling gem %s" % gemname)
        self.config = cp
        self.gemname = gemname
        self.rpmbuilddir = os.path.expanduser(cp.get('global','rpmbuilddir'))
        self.gemtemplate = os.path.expanduser(cp.get('global','gemtemplate'))
        self.tempdir = os.path.expanduser(cp.get('global','tempdir'))
        self.skipdeps = skipdeps
        #self.packagelog = os.path.expanduser(cp.get('packagelog'))
    
    
    def setupDirs(self):
        '''
        setup rpmbuild RPMS SOURCES SPECS
        '''
        dirs = [ '%s/SOURCES' % self.rpmbuilddir,
                 '%s/SPECS' % self.rpmbuilddir,
                 '%s/BUILD' % self.rpmbuilddir,
                 '%s/RPMS/noarch' % self.rpmbuilddir,
                 '%s/RPMS/x86_64' % self.rpmbuilddir,
                 '%s/BUILDROOT' % self.rpmbuilddir,
                 '%s/%s' % (self.tempdir, self.gemname),          
            ]
        for d in dirs:
            try:
                os.makedirs(d)
            except OSError, e:
                pass
        self.log.debug("Various dirs made OK.")
        
    def fetchGem(self):
        '''
        Fetches this gem from 
        '''
        cmd =  "cd %s/SOURCES ;  gem fetch %s " % (self.rpmbuilddir, self.gemname)
        self.log.debug("Command is %s" % cmd )
        (o, e) = _runtimedcommand(cmd)
        if o is not None and not e.startswith('ERR'):
            self.log.debug("Out is %s" % o)
            fields = o.split()
            nv = fields[1]
            self.version = nv[len(self.gemname)+1:]
            self.log.debug("Version is %s" % self.version)
            self.log.info("Gem %s-%s fetched." % (self.gemname, self.version) )
        else:
            self.log.warning("Error/problem fetching %s" % self.gemname)
            raise GemBuildException('Problem fetching...')
   
   
    def makeSpec(self):
        '''
        gem2rpm -t $TEMPLATE  $gem-[0-9]*.gem > $RPMBUILDDIR/SPECS/rubygem-$gem.spec
        
        '''
        cmd =  "gem2rpm -t %s %s/SOURCES/%s-%s.gem > %s/SPECS/rubygem-%s.spec " % (
                                                                        self.gemtemplate,
                                                                        self.rpmbuilddir, 
                                                                        self.gemname,
                                                                        self.version,
                                                                        self.rpmbuilddir,
                                                                        self.gemname)
        self.log.debug("Command is %s" % cmd )
        (o, e) = _runtimedcommand(cmd)
        self.log.info("Created rubygem-%s.spec " % self.gemname)
        self.specfile = "%s/SPECS/rubygem-%s.spec" % ( self.rpmbuilddir, self.gemname)
    
    
    def fixSpec(self):
        '''
        '''
        #sf = open(self.specfile, 'w')
        #sf.close()
        
        
        
        
    def parseDeps(self):
        '''
        
        '''
        self.deps = []
        depset = set()
        cmd =  "cd %s/SOURCES ;  gem2rpm -d %s-%s.gem" % (self.rpmbuilddir, self.gemname, self.version)
        self.log.debug("Command is %s" % cmd )
        (o, e) = _runtimedcommand(cmd)
        if o is not None:
            self.log.debug("Out is %s" % o)
            o = o.strip()
            if len(o) > 3:
                lines = o.split('\n')
                for line in lines:
                    if len(line) > 3:
                        fields = line.split()
                        dep = fields[0]
                        if len(fields) > 2:                          
                            op = fields[1]
                            ver = fields[2]
                        self.log.debug("Dep is %s" % dep)
                    if dep.startswith('rubygem'):
                        depname = dep[8:-1]
                        self.log.debug("Adding dependency %s" % depname)
                        depset.add(depname)
            else:
                self.log.debug("No dependencies.")
        self.deps = list(depset)  
        
    def buildRPM(self):
        '''
    rpmbuild -bb $RPMBUILDDIR/SPECS/rubygem-$gem.spec    
        '''
        self.log.debug("Building gem %s" % self.gemname)
        cmd =  "rpmbuild -bb %s/SPECS/rubygem-%s.spec" % (self.rpmbuilddir, 
                                                          self.gemname)
        self.log.debug("Command is %s" % cmd )
        (o,e) = _runtimedcommand(cmd)
        if o is not None:
            self.log.info("RPM for rubygem-%s built OK." % self.gemname)
        elif 'error: Arch dependent binaries in noarch package' in e:
            self.log.warning('Native package, fixing and building...')
            self.buildNativeRPM()   
        else:
            self.log.error("Problem building RPM for rubygem-%s." % self.gemname)
            GemHandler.problemgems.add(self.gemname)
            raise GemBuildException('Problem building RPM.')
    
    def convertSpecNative(self):
        '''
        Fixes spec for this gem to Arch: x86_64
        '''
        self.log.debug("Converting %s spec to native..." % self.gemname)
        sf = open(self.specfile, 'r')
        linelist = sf.readlines()
        sf.close()

        sf2 = open(self.specfile, 'w')
        for line in linelist:
            line = line.replace('BuildArch: noarch' , 'BuildArch: x86_64')
            sf2.write(line)
        sf2.close()
    
    
    def buildNativeRPM(self):
        '''
        Converts spec to Arch: x86-64 and re-builds. 
        
        '''
        self.log.debug("Building gem %s native..." % self.gemname)
        self.convertSpecNative()
        self.buildRPM()
    
    
    def handleDeps(self):
        '''
        
        '''
        for dep in self.deps:
            self.log.debug('Processing dep %s' % dep)
            if dep not in GemHandler.handledgems:
                gh = GemHandler(self.config, dep)
                gh.handleGem()
            else:
                self.log.debug("Gem %s already done." % dep)
        self.log.info("Finished handling deps for %s" % self.gemname)
    
        
    def handleGem(self):
        self.setupDirs()
        try:
            self.fetchGem()
            self.makeSpec()
            self.fixSpec()
            self.buildRPM()
            self.log.debug("Adding gem %s to done list." % self.gemname)
            GemHandler.handledgems.add(self.gemname)
            if not self.skipdeps:
                self.parseDeps()
                self.handleDeps()
        except GemBuildException, e:
            self.log.error('Problem building gem %s: Error: %s' % (self.gemname, e) )


class GemRPMCLI(object):
    
    def __init__(self):
        self.parseopts()
        self.setuplogging()
                
        
    def setuplogging(self):
        self.log = logging.getLogger()
        FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(name)s %(filename)s:%(lineno)d %(funcName)s(): %(message)s'
        formatter = logging.Formatter(FORMAT)
        #formatter.converter = time.gmtime  # to convert timestamps to UTC
        logStream = logging.StreamHandler()
        logStream.setFormatter(formatter)
        self.log.addHandler(logStream)
    
        self.log.setLevel(logging.WARN)
        if self.results.debug:
            self.log.setLevel(logging.DEBUG)
        if self.results.info:
            self.log.setLevel(logging.INFO)
        self.log.info('Logging initialized.')


    def parseopts(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-c', '--config', 
                            action="store", 
                            dest='configpath', 
                            default='~/etc/rubygemrpm.conf', 
                            help='configuration file path.')
        
        parser.add_argument('-d', '--debug', 
                            action="store_true", 
                            dest='debug', 
                            help='debug logging')        

        parser.add_argument('-v', '--verbose', 
                            action="store_true", 
                            dest='info', 
                            help='info logging')  
        
        parser.add_argument('-s', '--skipdeps', 
                            action="store_true",
                            default = False, 
                            dest='skipdeps', 
                            help='skip building deps recursively')  
        
        parser.add_argument('gemname', 
                             action="store")
        
        
        self.results= parser.parse_args()
        print(self.results)

    def invoke(self):
        cp = ConfigParser()
        ns = self.results
        self.log.info("Config is %s" % ns.configpath)
        cp.read(os.path.expanduser(ns.configpath))
        gh = GemHandler(cp, ns.gemname, skipdeps=ns.skipdeps)
        gh.handleGem()
        self.log.info("Handled %d gems: %s" % ( len(GemHandler.handledgems),
                                                GemHandler.handledgems ))
        self.log.error("Problems with %d gems: %s" % (len(GemHandler.problemgems), 
                                                      GemHandler.problemgems))


if __name__ == '__main__':
    rgcli = GemRPMCLI()
    rgcli.invoke()
