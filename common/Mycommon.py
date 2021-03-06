#!/usr/bin/env python
# --*--coding:utf-8--*--

'''
This is my common functions 

'''
import os,sys,re  
import socket 
import struct 
import fcntl 
import psutil
import os.path
import fileinput

############
# cpu info #
############

def cpuinfo():
    '''
    return a dict contain  cpu count , cpu use percent

    '''
    d={}
    count=psutil.cpu_count()
    cpu_use='%0.2f' % psutil.cpu_percent()
    cpu_use_per=psutil.cpu_percent(percpu=True)
    cpu_use_per=[ float('%d'%x) for x in cpu_use_per ]
    d['count']=count
    d['cpu_use']=cpu_use
    d['cpu_use_per']=cpu_use_per
    return d

############
# mem info #
############

def meminfo(all=False,unit='KB'):
    '''
    return a dict contain mem total , mem free , cached , swap ; only for linux

    '''
    d={}
    with open('/proc/meminfo') as f:
        for line in f:
            key=line.split(':')[0].strip()
            num=line.split(':')[1].strip().split()[0]
            num=float(num)
            if unit == 'KB':
                value='%0.2f KB' % num
            elif unit == 'MB':
                value='%0.2f MB' % (num/1024)
            elif unit == 'GB':
                value='%0.2f GB' % (num/1024/1024)
            d[key] = value
    if all == False:
        d={'MemTotal': d['MemTotal'],
           'MemFree': d['MemFree'], 
           'Buffers': d['Buffers'],
           'Cached': d['Cached'],
           'SwapTotal': d['SwapTotal'],
           'SwapFree': d['SwapFree']
           }
    return d

#############
# disk info #
#############

def diskinfo():
    d={}
    lt=[]
    l=psutil.disk_partitions()
    for i in l:
        t=[ x for x in i ]
        lt.append(t)
    d['partition']=lt
    d['io_counters']=psutil.disk_io_counters(perdisk=False)
    return d

#############
# net  info #
#############

def get_hostname():
    '''
    Get fully qualified domain name from name

    '''
    return socket.getfqdn()
    
def get_ip_old(name):
    '''
    get interface IP address for linux
   
    >>>import Mycommon
    >>>Mycommon.get_ip('eth0')
    '10.0.1.22'

    '''
    s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15]))[20:24])

def get_ip(name='eth0',netmask=False):
    '''
    get interface IP address for linux

    '''
    l=[]
    cmdstr='/sbin/ifconfig | grep %s -A 1' % name
    f=os.popen(cmdstr)
    f=f.read()
    ip_reg=r'([0-9]{1,3}.){3}[0-9]{1,3}'
    addr_reg=r'inet addr:%s' % ip_reg
    mask_reg=r'Mask:%s' % ip_reg
    ip_pattern=re.compile(ip_reg)
    addr_pattern=re.compile(addr_reg)
    mask_pattern=re.compile(mask_reg)
    m=re.search(addr_pattern,f)
    n=re.search(mask_pattern,f)
    if m:
        ip_str=re.search(ip_pattern,m.group()).group()
    else:
        ip_str=''
    if netmask == True:
        if n:
            mask_str=re.search(ip_pattern,n.group()).group()
        else:
            mask_str=''
        ip_str='%s/%s' % (ip_str,mask_str)
    return ip_str
    
def get_mac(name='eth0'):
    '''
    get interface HWADDR for linux

    '''
    cmdstr='/sbin/ifconfig | grep %s -A 1' % name
    f=os.popen(cmdstr)
    f=f.read()
    mac_reg='([0-9a-zA-Z]{1,2}\:){5}[0-9a-zA-Z]{1,2}'
    addr_reg='HWaddr %s' % mac_reg
    mac_pattern=re.compile(mac_reg)
    addr_pattern=re.compile(addr_reg)
    m=re.search(addr_pattern,f)
    if m:
        mac_str=re.search(mac_pattern,m.group()).group()
    else:
        mac_str=''
    return mac_str
def get_interface(name='eth0'):
    '''
    get interface info

    '''
    d={}
    ipaddr=get_ip(name,netmask=True).split('/')[0]
    netmask=get_ip(name,netmask=True).split('/')[1]
    hwaddr=get_mac(name)
    d['mac']=hwaddr
    d['ip']=ipaddr
    d['netmask']=netmask
    return d
def tcp_connection():
    '''
    get tcp connections 

    '''
    tcp_files=['/proc/net/tcp','/proc/net/tcp6']
    exists_tcp_files=[]
    for f in tcp_files:
        if os.path.isfile(f):
            exists_tcp_files.append(f)
    result = []
    fh = fileinput.input(exists_tcp_files)
    for line in fh:
        if line and ( 'address' not in line ):
            result.append(line.split()[3])
    conn_types = {
            #'ERROR':'00',
            'ESTABLISHED':'01',
            #'SYN_SENT':'02',
            'SYN_RECV':'03',
            'FIN_WAIT1':'04',
            'FIN_WAIT2':'05',
            'TIME_WAIT':'06',
            #'CLOSE':'07',
            'CLOSE_WAIT':'08',
            'LAST_ACK':'09',
            #'LISTEN':'0A',
            #'CLOSING':'0B',
            }
    TOTAL = {}
    TOTAL_CONN = 0 
    for k,v in conn_types.iteritems():
        c = result.count(v)
        TOTAL_CONN += c
        TOTAL[k] = c 
    TOTAL['TOTAL_CONN'] = TOTAL_CONN
    return TOTAL
def get_tcp_value(name):
    '''
    get tcp kernel value

    '''
    tcp_file = '/proc/sys/net/ipv4/%s' % name
    with open(tcp_file) as f:
        v = f.read().strip()
    return v
    

