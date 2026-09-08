#!/usr/bin/env python3
"""Plot exact bin minima of the two complete certified finite streams.

The CSV retains integer floors and inclusive bin endpoints. The drawing
is illustrative; it is not consumed by the mathematical certificate.
"""
import argparse
import csv
import fcntl
import os
from pathlib import Path
import tempfile
from verify_finite import c_rows, rust_rows, ERROR

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original',type=Path);p.add_argument('independent',type=Path)
    p.add_argument('output',type=Path);p.add_argument('--lock',type=Path,required=True)
    args=p.parse_args()
    with args.lock.open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        first=690988;last=3840000;width=2048;bins=[];current=None
        c=iter(c_rows(args.original));r=iter(rust_rows(args.independent))
        for n in range(first,last+1):
            cn,cv=next(c);rn,rv=next(r)
            if cn!=rn or cn!=n: raise ValueError('plot coverage')
            bucket=(n-first)//width
            if current!=bucket:
                bins.append([n,n,cv,rv]);current=bucket
            else:
                bins[-1][1]=n;bins[-1][2]=min(bins[-1][2],cv);bins[-1][3]=min(bins[-1][3],rv)
        if next(c,None) is not None or next(r,None) is not None: raise ValueError('extra plot rows')
        args.output.mkdir(parents=True,exist_ok=True)
        with (args.output/'finite-floors.csv').open('w') as f:
            w=csv.writer(f);w.writerow(['first_N','last_N','original_minimum12','independent_minimum12']);w.writerows(bins)
        with tempfile.TemporaryDirectory(prefix='rh-q2-matplotlib-') as config:
            os.environ['MPLCONFIGDIR']=config
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                                 'svg.hashsalt':'rh-q2-finite-floors'})
            fig,ax=plt.subplots(figsize=(8,4.6),layout='constrained')
            x=[row[0]/1e6 for row in bins]+[(last+1)/1e6]
            for column,color,label,style in [(2,'#235789','Original C','-'),(3,'#d17c19','Independent Rust','--')]:
                y=[row[column]/1e12 for row in bins];y.append(y[-1])
                ax.step(x,y,where='post',color=color,label=label,linewidth=1.3,linestyle=style)
            ax.axhline(float(ERROR),color='#333333',linewidth=1,linestyle=':',label='Uniform error ceiling')
            for n in (729000,819000,1028000): ax.axvline(n/1e6,color='#b4b4b4',linewidth=.6,zorder=0)
            ax.set(xlabel=r'Cutoff $N$ (millions)',ylabel='Certified lower bound',yscale='log',xlim=(first/1e6,last/1e6))
            ax.grid(axis='y',which='major',alpha=.18)
            ax.legend(frameon=False,loc='center right')
            ax.set_title('Two complete finite verifications',loc='left',pad=12)
            fig.text(.012,-.035,'Each step is the minimum certified floor over an inclusive bin of at most 2,048 indices.',fontsize=9)
            fig.savefig(args.output/'finite-floors.svg',bbox_inches='tight',metadata={'Date':None})
            fig.savefig(args.output/'finite-floors.pdf',bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
            fig.savefig(args.output/'finite-floors.png',dpi=160,bbox_inches='tight')
            plt.close(fig)
        print(f'PASS: {len(bins)} exact bins cover all {last-first+1} indices; SVG/PDF/PNG written')

if __name__=='__main__': main()
