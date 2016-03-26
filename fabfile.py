from fabric.api import run, env, sudo, put, cd as _cd
from fabric.decorators import parallel, hosts
from fabric.operations import put
from fabric.contrib.files import append, exists
import configuration
import os.path

config = configuration.Configuration.load('./config.json')
authorized_keys = '~/.ssh/authorized_keys'

env.use_ssh_config = True
env.hosts = config.get('hosts', [])

def setup():
    update_upgrade()
    make_ssh_dir()
    upload_public_keys()
    upload_ssh_config()
    upload_internal_key()
    setup_fstabs()
    set_hostname()

def install():
    install_tmux()
    install_git()
    install_build_essentials()
    install_java8()

def install_git():
    sudo('apt-get install -y git-core')

def install_julia():
    with cd('~/projects'):
        download_and_untar_into('https://status.julialang.org/download/linux-arm', 'julia.tar.gz', 'julia')

def install_spark():
    with cd('~/projects'):
        download_and_untar_into('http://www.apache.org/dist/spark/spark-1.6.1/spark-1.6.1-bin-hadoop2.6.tgz', 'spark.tar.gz', 'spark')

def install_java8():
    sudo('apt-get install -y oracle-java8-jdk')

def change_password():
    sudo('passwd pi')

def upload_ssh_config():
    put('./ssh_config', '~/.ssh/config')

def upload_internal_key():
    put('./raspberry-internal*', '~/.ssh', mode=0600)
    append_files_content_to(['./raspberry-internal.pub'], authorized_keys)

def upload_public_keys():
    pub_keys = config.get('ssh_public_keys', [])
    append_files_content_to(pub_keys, authorized_keys)

def set_hostname():
    sudo('echo %s > /etc/hostname' % env.host_string)
    append('/etc/hosts', '127.0.0.1 %s' % env.host_string, use_sudo=True)

def setup_fstabs():
    sudo('apt-get install -y cifs-utils')
    sudo('mkdir -p /mnt/readyshare')
    fstab_file = '/etc/fstab'
    fstabs = config.get('fstabs', [])
    for fstab in fstabs:
        append(fstab_file, fstab, use_sudo=True)
    sudo('mount -a')

def install_build_essentials():
    sudo('apt-get install -y build-essential distcc')

def install_tmux():
    sudo('apt-get install -y tmux')

def make_projects_dir():
    run('mkdir -p ~/projects')

def make_ssh_dir():
    run('mkdir -p ~/.ssh')

def update_upgrade():
    sudo('apt-get update; apt-get -y upgrade')

def download_and_untar_into(url, gz, dst):
    if not exists(dst):
        run('curl -L -o %s %s' % (gz, url))
        run('mkdir -p %s' % dst)
        run('tar -zxvf %s -C %s --strip-components=1' % (gz, dst))
        run('rm %s' % gz)

def append_files_content_to(srcs, dst):
    for src in srcs:
        with open(os.path.expanduser(src)) as source:
            content = source.read().strip()
            append(dst, content)

def cd(path):
   run('mkdir -p %s' % path) 
   return _cd(path)
