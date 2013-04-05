#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
ponysay - Ponysay, cowsay reimplementation for ponies

Copyright (C) 2012, 2013  Erkin Batu Altunbaş et al.


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


If you intend to redistribute ponysay or a fork of it commercially,
it contains aggregated images, some of which may not be commercially
redistribute, you would be required to remove those. To determine
whether or not you may commercially redistribute an image make use
that line ‘FREE: yes’, is included inside the image between two ‘$$$’
lines and the ‘FREE’ is and upper case and directly followed by
the colon.
'''
from common import *



'''
KMS support utilisation
'''
class KMS():
    '''
    Identifies whether KMS support is utilised
    
    @param   linuxvt:bool  Whether Linux VT is used
    @return  :bool         Whether KMS support is utilised
    '''
    @staticmethod
    def usingkms(linuxvt):
        ## KMS is not utilised if Linux VT is not used
        if not linuxvt:
            return False
        
        ## Read the PONYSAY_KMS_PALETTE environment variable
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        ## Read the PONYSAY_KMS_PALETTE_CMD environment variable, and run it
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        ## If the palette string is empty KMS is not utilised
        return env_kms != ''
    
    
    '''
    Returns the file name of the input pony converted to a KMS pony, or if KMS is not used, the input pony itself
    
    @param   pony:str      Choosen pony file
    @param   home:str      The home directory
    @param   linuxvt:bool  Whether Linux VT is used
    @return  :str          Pony file to display
    '''
    @staticmethod
    def kms(pony, home, linuxvt):
        ## If not in Linux VT, return the pony as is
        if not linuxvt:
            return pony
        
        ## KMS support version constant
        KMS_VERSION = '2'
        
        ## Read the PONYSAY_KMS_PALETTE environment variable
        env_kms = os.environ['PONYSAY_KMS_PALETTE'] if 'PONYSAY_KMS_PALETTE' in os.environ else None
        if env_kms is None:  env_kms = ''
        
        ## Read the PONYSAY_KMS_PALETTE_CMD environment variable, and run it
        env_kms_cmd = os.environ['PONYSAY_KMS_PALETTE_CMD'] if 'PONYSAY_KMS_PALETTE_CMD' in os.environ else None
        if (env_kms_cmd is not None) and (not env_kms_cmd == ''):
            env_kms = Popen(shlex.split(env_kms_cmd), stdout=PIPE, stdin=sys.stderr).communicate()[0].decode('utf8', 'replace')
            if env_kms[-1] == '\n':
                env_kms = env_kms[:-1]
        
        ## If not using KMS, return the pony as is
        if env_kms == '':
            return pony
        
        ## Store palette string and a clone with just the essentials
        palette = env_kms
        palettefile = env_kms.replace('\033]P', '')
        
        ## Get and in necessary make cache directory
        cachedir = '/var/cache/ponysay'
        shared = True
        if not os.path.isdir(cachedir):
            cachedir = home + '/.cache/ponysay'
            shared = False
            if not os.path.isdir(cachedir):
                os.makedirs(cachedir)
        _cachedir = '\'' + cachedir.replace('\'', '\'\\\'\'') + '\''
        
        ## KMS support version control, clean everything if not matching
        newversion = False
        if not os.path.isfile(cachedir + '/.version'):
            newversion = True
        else:
            with open(cachedir + '/.version', 'rb') as cachev:
                if cachev.read().decode('utf8', 'replace').replace('\n', '') != KMS_VERSION:
                    newversion = True
        if newversion:
            for cached in os.listdir(cachedir):
                cached = cachedir + '/' + cached
                if os.path.isdir(cached) and not os.path.islink(cached):
                    shutil.rmtree(cached, False)
                else:
                    os.remove(cached)
            with open(cachedir + '/.version', 'w+') as cachev:
                cachev.write(KMS_VERSION)
                if shared:
                    try:
                        os.chmod(cachedir + '/.version', 0o7777)
                    except:
                        pass
        
        ## Get kmspony directory and kmspony file
        kmsponies = cachedir + '/kmsponies/' + palettefile
        kmspony = kmsponies + '/' + pony
        
        ## If the kmspony is missing, create it
        if not os.path.isfile(kmspony):
            ## kmspony directory
            kmsponydir = kmspony[:kmspony.rindex('/')]
            
            ## Change file names to be shell friendly
            _kmspony = '\'' + kmspony.replace('\'', '\'\\\'\'') + '\''
            _pony    = '\'' +    pony.replace('\'', '\'\\\'\'') + '\''
            
            ## Create kmspony
            if not os.path.isdir(kmsponydir):
                os.makedirs(kmsponydir)
                if shared:
                    Popen('chmod -R 7777 -- %s/kmsponies' % _cachedir, shell=True).wait()
            opts = '--balloon n --left - --right - --top - --bottom -'
            ponytoolcmd = 'ponytool --import ponysay --file %%s %s --export ponysay --file %%s --platform linux %s' % (opts, opts)
            ponytoolcmd += ' --colourful y --fullcolour y --palette %s'
            if not os.system(ponytoolcmd % (_pony, _kmspony, palette)) == 0:
                printerr('Unable to run ponytool successfully, you need util-say>=3 for KMS support')
                exit(1)
            if shared:
                try:
                    os.chmod(kmspony, 0o7777)
                except:
                    pass
        
        return kmspony

