"""Download exact public FJSP files and verify upstream git blob hashes.
CI has internet; offline users may place same verified files under data/.
"""
import argparse,hashlib,urllib.request
from pathlib import Path

FILES={
 'mk02':('https://raw.githubusercontent.com/SchedulingLab/fjsp-instances/main/brandimarte/mk02.txt','0155615dc3e5ffd99a73f35a3432151efa8ef2c8'),
 'mk03':('https://raw.githubusercontent.com/SchedulingLab/fjsp-instances/main/brandimarte/mk03.txt','10700055be30bced61ea02c371c4695bf852bfc7'),
}

def git_blob_sha(raw):
 return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def download(name,target):
 url,expected=FILES[name]; target=Path(target)
 if target.exists() and git_blob_sha(target.read_bytes())==expected:return {'name':name,'verified':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'cached':True}
 with urllib.request.urlopen(url,timeout=40) as response: raw=response.read()
 got=git_blob_sha(raw)
 if got != expected:raise ValueError(f'{name}: upstream blob hash mismatch: {got} != {expected}')
 target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 return {'name':name,'verified':True,'sha256':hashlib.sha256(raw).hexdigest(),'cached':False}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--names',nargs='+',choices=FILES,default=['mk02','mk03']);a=p.parse_args()
 for n in a.names:print(download(n,f'data/{n}.txt'))
