# coding:utf-8

'''
@author = super_fazai
@File    : linux_utils.py
@Time    : 2018/7/13 18:14
@connect : superonesfazai@gmail.com
'''

__all__ = [
    'daemon_init',                                      # 守护进程
    'restart_program',                                  # 初始化避免异步导致log重复打印
    'process_exit',                                     # 判断进程是否存在
    'kill_process_by_name',                             # 根据进程名杀掉对应进程(linux/mac测试通过!)
    'get_os_platform',                                  # 返回当前是什么系统

    # shell
    'get_str_from_command',                             # shell下执行成功的命令有正常输出,执行不成功的命令得不到输出,得到输出为""
    'get_current_file_path',                            # 得到当前文件的绝对路径

    # github
    'auto_git',                                         # master 自动 git
]

def daemon_init(stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
    '''
    杀掉父进程，独立子进程
    :param stdin:
    :param stdout:
    :param stderr:
    :return:
    '''
    import sys
    import os

    sys.stdin = open(stdin, 'r')
    sys.stdout = open(stdout, 'a+')
    sys.stderr = open(stderr, 'a+')
    try:
        pid = os.fork()
        if pid > 0:     # 父进程
            os._exit(0)
    except OSError as e:
        sys.stderr.write("first fork failed!!" + e.strerror)
        os._exit(1)

    # 子进程， 由于父进程已经退出，所以子进程变为孤儿进程，由init收养
    '''setsid使子进程成为新的会话首进程，和进程组的组长，与原来的进程组、控制终端和登录会话脱离。'''
    os.setsid()
    '''防止在类似于临时挂载的文件系统下运行，例如/mnt文件夹下，这样守护进程一旦运行，临时挂载的文件系统就无法卸载了，这里我们推荐把当前工作目录切换到根目录下'''
    os.chdir("/")
    '''设置用户创建文件的默认权限，设置的是权限“补码”，这里将文件权限掩码设为0，使得用户创建的文件具有最大的权限。否则，默认权限是从父进程继承得来的'''
    os.umask(0)

    try:
        pid = os.fork()  # 第二次进行fork,为了防止会话首进程意外获得控制终端
        if pid > 0:
            os._exit(0)  # 父进程退出
    except OSError as e:
        sys.stderr.write("second fork failed!!" + e.strerror)
        os._exit(1)

    # 孙进程
    #   for i in range(3, 64):  # 关闭所有可能打开的不需要的文件，UNP中这样处理，但是发现在python中实现不需要。
    #       os.close(i)
    sys.stdout.write("Daemon has been created! with pid: %d\n" % os.getpid())
    sys.stdout.flush()  # 由于这里我们使用的是标准IO，这里应该是行缓冲或全缓冲，因此要调用flush，从内存中刷入日志文件。

def restart_program():
    '''
    初始化避免异步导致log重复打印
    :return:
    '''
    import sys
    import os

    python = sys.executable
    os.execl(python, python, *sys.argv)

def process_exit(process_name):
    '''
    判断进程是否存在
    :param process_name:
    :return: 0 不存在 | >= 1 存在
    '''
    import os

    # Linux
    process_check_response = os.popen('ps aux | grep "' + process_name + '" | grep -v grep').readlines()

    return len(process_check_response)

def kill_process_by_name(process_name):
    '''
    根据进程名杀掉对应进程(linux/mac测试通过!)
    :param process_name: str
    :return:
    '''
    import os
    from .common_utils import delete_list_null_str

    if process_exit(process_name) > 0:
        try:
            process_check_response = os.popen('ps aux | grep ' + process_name).readlines()
            # print(process_check_response)
            for item in process_check_response:
                # print(item)
                tmp = delete_list_null_str(item.split(' '))[1]      # 得到进程号pid, 并杀掉每一个
                # print(tmp)

                os.system('kill -9 {0}'.format(tmp))
                print('该进程名%s, pid = %s, 进程kill完毕!!' % (process_name, tmp))

        except Exception as e:
            print(e)
    else:
        print('进程[%s]不存在' % process_name)

def get_str_from_command(cmd):
    '''
    # 执行成功的命令有正常输出,执行不成功的命令得不到输出,得到输出为"",eg.command=which nihao
    # 判断程序有没有已经安装可eg.get_string_from_command("sqlmap --help")
    :param cmd:
    :return:
    '''
    import subprocess

    return subprocess.getstatusoutput(cmd)[1]

def get_current_file_path():
    '''
    # 得到当前文件的绝对路径
    :return:
    '''
    import os

    tmp_path = os.path.abspath(__file__)
    module_path = tmp_path[:-len(__file__.split("/")[-1])]

    return module_path

def auto_git(path):
    '''
    master 自动git
    :param path: 绝对路径
    :return:
    '''
    import os
    import time
    import re
    from .time_utils import get_shanghai_time

    os.system('cd {0} && git pull'.format(path))
    print('------>>>| 远程合并分支完毕!!!')
    print((path + ' 正在提交').center(100, '*'))
    os.popen('cd {0} && git add --all'.format(path))
    time.sleep(2)
    now_time = str(get_shanghai_time())
    now_time = str(re.compile(r'\..*').sub('', now_time))
    os.system('cd {0} && git commit -m "{1}"'.format(path, now_time))
    time.sleep(2)
    os.system('cd {0} && git push -u origin master'.format(path))
    print((path + ' 提交成功!!').center(100, '*') + '\n')

    return True

def get_os_platform():
    '''
    返回当前是什么系统
    :return: mac是darwin | ...
    '''
    import os
    import sys

    if "_PYTHON_HOST_PLATFORM" in os.environ:
        return os.environ["_PYTHON_HOST_PLATFORM"]

    if sys.platform.startswith('osf1'):
        return 'osf1'

    return sys.platform
