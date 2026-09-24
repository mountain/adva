"""Original figures from retained aggregate evidence; Unknown v0.3."""
import hashlib
import json
from pathlib import Path


def run(contract, output):
    import matplotlib
    assert matplotlib.__version__ == contract['matplotlib']
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'svg.fonttype':'none', 'svg.hashsalt':'adva-0229',
                         'font.size':10, 'axes.spines.top':False, 'axes.spines.right':False})
    root = Path(__file__).parent
    output.mkdir(parents=True, exist_ok=True)
    metadata = {'Date':None, 'Creator':'Codex (OpenAI); original Adva research 0229'}
    cases = json.loads((root/'phase1.json').read_text())['results']['cases']
    fig, axes = plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for ax, row in zip(axes, cases):
        for key, label, color in [('ar1','Coarse, one step','#b34732'),
                                   ('ar3','Coarse, three steps','#286c99'),
                                   ('fine_coarse','Fine spectral state','#237e64')]:
            ax.plot(range(1,25),np.maximum(row['nmse_by_lead'][key],1e-32),label=label,color=color)
        ax.set_yscale('log');ax.set_ylim(1e-32,10)
        ax.set_xlabel('Forecast lead (synthetic steps)')
        ax.set_title('Pure transport' if row['diffusion']==0 else 'Transport plus diffusion')
        ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Normalized squared error; display floor 1e-32')
    axes[1].legend(loc='center right')
    fig.suptitle('Aliasing can look like damping\nDeclared noiseless fixtures; this is not a weather forecast',fontsize=12)
    first=output/'synthetic-aliasing.svg';assert not first.exists()
    fig.savefig(first,metadata=metadata);plt.close(fig)
    rows=json.loads((root/'xue-evidence.json').read_text())['results']['rows']
    fig,axes=plt.subplots(1,3,figsize=(12,4.8),layout='constrained')
    for ax,patch in zip(axes,['East Asia','North America','Middle East']):
        chosen=[next(r for r in rows if r['patch']==patch and r['degree']==d and r['model']==m and r['lead_months']==1)
                for d,m in [(6,'joint'),(12,'joint'),(12,'climatology')]]
        coarse=[r['coarse_mse'] for r in chosen];detail=[r['detail_mse'] for r in chosen]
        ax.bar(range(3),coarse,color='#286c99',label='Retained by block average')
        ax.bar(range(3),detail,bottom=coarse,color='#e5a544',label='Within-block residual')
        ax.set_xticks(range(3),['L6\njoint','L12\njoint','L12\nseasonal'])
        ax.set_title(patch);ax.set_ylim(0,60);ax.grid(axis='y',alpha=.2)
        for x,r in enumerate(chosen):
            ax.text(x,r['vector_mse']+1,f"{r['vector_rmse']:.2f}",ha='center',fontsize=10)
    axes[0].set_ylabel('Area-weighted vector MSE (m2/s2)')
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside lower center',ncol=2)
    fig.suptitle('Frozen xue development backtests, 2020-2025; one-month lead\nNumbers above bars: vector RMSE (m/s). Reference: NCEP/NCAR R1 via NOAA PSL.\nFixed 9 x 9 patches; data authenticity remains unverified.',fontsize=11)
    second=output/'xue-error-decomposition.svg';assert not second.exists()
    fig.savefig(second,metadata=metadata);plt.close(fig)
    return {'files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
                      for p in [first,second]], 'scope':'Rendering retained results only; no new fitting, selection or experiment.'}
