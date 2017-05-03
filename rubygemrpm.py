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
    log = logging.getLogger()
    before = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = None
    (out, err) = p.communicate()
    delta = time.time() - before
    log.debug('%s seconds to perform command' %delta)
    if p.returncode == 0:
        log.debug('Leaving with OK return code.')
    else:
        log.warning('Leaving with bad return code. rc=%s err=%s out=%s' %(p.returncode, err, out ))
        out = None
    return out



class GemHandler(object):
    
    def __init__(self, cp , gemname):
        self.log = logging.getLogger()
        self.log.info("Handling gem %s" % gemname)
        self.gemname = gemname
        self.rpmbuilddir = os.path.expanduser(cp.get('global','rpmbuilddir'))
        self.gemtemplate = os.path.expanduser(cp.get('global','gemtemplate'))
        self.tempdir = os.path.expanduser(cp.get('global','tempdir'))
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
        '''
        cmd =  "cd %s/SOURCES ;  gem fetch %s " % (self.rpmbuilddir, self.gemname)
        self.log.debug("Command is %s" % cmd )
        o = _runtimedcommand(cmd)
        if o is not None:
            self.log.debug("Out is %s" % o)
            fields = o.split()
            nv = fields[1]
            self.version = nv[len(self.gemname)+1:]
            self.log.debug("Version is %s" % self.version)

   
    def makeSpec(self):
        '''
        
        '''
    
    def fixSpec(self):
        '''
        '''
        
    def parseDeps(self):
        '''
        
        '''
        self.deps = []
        cmd =  "cd %s/SOURCES ;  gem2rpm -d %s-%s.gem" % (self.rpmbuilddir, self.gemname, self.version)
        self.log.debug("Command is %s" % cmd )
        o = _runtimedcommand(cmd)
        if o is not None:
            self.log.debug("Out is %s" % o)
            lines = o.split('\n')
            for line in lines:
                (dep, op, ver) = line.split()
                self.log.debug("Dep is %s" % dep)
                
          
        
    def buildRPM(self):
        '''
        
        '''
    
    def parseDeps(self):
        '''
        '''    
        
    def handleGem(self):
        self.setupDirs()
        self.fetchGem()
        self.makeSpec()
        self.fixSpec()
        self.buildRPM()
        self.parseDeps()
        
        
        





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
        # adding a new Handler for the console, 
        # to be used only for DEBUG and INFO modes. 
        #if self.options.logLevel in [logging.DEBUG, logging.INFO]:
        #    if self.options.console:
        #        console = logging.StreamHandler(sys.stdout)
        #        console.setFormatter(formatter)
        #        console.setLevel(self.options.logLevel)
        #        self.log.addHandler(console)
        #self.log.setLevel(self.options.logLevel)
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
        
        parser.add_argument('gemname', 
                             action="store")
        
        
        self.results= parser.parse_args()
        #print(self.results)

    def invoke(self):
        cp = ConfigParser()
        ns = self.results
        self.log.info("Config is %s" % ns.configpath)
        cp.read(os.path.expanduser(ns.configpath))
        gh = GemHandler(cp, ns.gemname)
        gh.handleGem()




if __name__ == '__main__':
    rgcli = GemRPMCLI()
    rgcli.invoke()
