'''
Need to install pysftp 0.2.9
https://pypi.org/project/pysftp/
'''

import pysftp
import argparse
import os
import subprocess
import sys

'''
Display
'''
def ShowProgress(current_file_index, total_file_count, filepath):  
  sys.stdout.write("\rUploading: {0}/{1}:{2}".format(current_file_index, total_file_count, filepath))
  sys.stdout.flush()

'''
Local
'''
def ReadArgs():
  parser = argparse.ArgumentParser(description=':: Zemmy Git to FTP Deployment ::')
  parser.add_argument('-m','--mode', help='Transfer Mode',required=True)
  parser.add_argument('-t','--target', help='Target Host',required=True)
  parser.add_argument('-d','--directory', help='Root Folder',required=True)
  parser.add_argument('-u','--username', help='Username to login',required=True)
  parser.add_argument('-p','--password',help='Password to login', required=True)
  return parser.parse_args()

# for value in AbsoluteFilePaths(project_dir):
def AbsoluteFilePaths(directory):
  for dirpath,_,filenames in os.walk(directory):
    for f in filenames:
      yield os.path.abspath(os.path.join(dirpath, f))

'''
GIT
'''
def ExecCommand(command, param):
  pipe_result = subprocess.run([command, param], stdout=subprocess.PIPE)
  pipe_utf8 = pipe_result.stdout.decode('utf-8')
  return pipe_utf8.splitlines()

def GetGitStatus(string):
  status = ''
  for line in string:
    if 'nothing to commit, working tree clean' in line: 
      status = 'clean'
    else:
      status = 'dirty'
  return status

def CheckGitStatus():
  git_line_array = ExecCommand('git', 'status')
  git_status = GetGitStatus(git_line_array)
  if git_status == 'clean':
    ProcessSFTPTransfer()
  else:
    print('Cannot countinue because the repository is not in clean state!')

def GetGitDeleteList():
  pipe_result = subprocess.run(['git', 'diff --name-status '], stdout=subprocess.PIPE)

'''
SFTP
'''
def PushAllFileToServer(srv):
  # project_dir = os.getcwd()
  # for value in AbsoluteFilePaths(project_dir):
    # sftp.cd('public')
    # print(value)
  git_line_array = ExecCommand('git', 'ls-files')
  srv.chdir(args.directory)
  for line in git_line_array:
    ShowProgress(5, 100, line)
    full_path = os.path.join(args.directory, line)
    folder = os.path.dirname(full_path)
    srv.makedirs(folder)
    srv.chdir(folder)
    srv.put(line)

  # data = srv.listdir()
  # for i in data:
  #   print(i)

def ProcessSFTPTransfer():
  '''
  if mode init will push all local repo to server
    search for config file on server first, if found and valid, ask for re-upload confirmation
  if mode sync will read config file on server and compare with local repo
    read config file
      if not found, show notification and then re-upload all
    compare and get diffence
      delete file from server
      upload (create and replace) file on server
  '''
  # Init connection
  cnopts = pysftp.CnOpts()
  cnopts.hostkeys = None
  srv = pysftp.Connection(args.target, username=args.username, password=args.password, cnopts=cnopts)

  if args.mode == '1':  #init. Push all
    PushAllFileToServer(srv)

  # srv.close()


# Main runtime
args = ReadArgs()
# git_status = CheckGitStatus()
CheckGitStatus()
# if git_status

'''
data = srv.listdir()

for i in data:
    print(i)
'''