import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'src'))
from qa_public import fetch_archive
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='data/steel_plates_faults_uci198.zip');a=p.parse_args()
    print(json.dumps(fetch_archive(a.out),indent=2))
