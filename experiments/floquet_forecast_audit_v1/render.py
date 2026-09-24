"""Original aggregate Floquet audit chart, no field images or external assets."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def render(r,out):
 plt.rcParams.update({'svg.fonttype':'none','font.size':10})
 fig,axs=plt.subplots(1,3,figsize=(15,4.6),layout='constrained')
 theta=np.linspace(0,2*np.pi,361);axs[0].plot(np.cos(theta),np.sin(theta),'--',color='#888888',lw=1)
 modes=r['modes'];axs[0].scatter([m['monthly_real'] for m in modes],[m['monthly_imag'] for m in modes],s=18,c='#006e82')
 axs[0].axhline(0,color='#dddddd',lw=.6);axs[0].axvline(0,color='#dddddd',lw=.6);axs[0].set(xlim=(-1.08,1.08),ylim=(-1.08,1.08),aspect='equal',xlabel='Real part',ylabel='Imaginary part',title='One-step latent eigenvalues')
 rows=r['gains'];months=[x['months'] for x in rows]
 for key,label,color in [('latent_operator_norm','Latent maximum gain','#006e82'),('full_encoded_operator_norm','Full encoded maximum gain','#a85922'),('spectral_radius_power','Monthly spectral radius ^ n','#788d4e')]:
  axs[1].plot(months,[x[key] for x in rows],marker='o',ms=3,label=label,color=color)
 axs[1].axhline(1,color='#777777',ls='--',lw=1);axs[1].set(xlabel='Repeated one-step months',ylabel='Normalized Euclidean amplitude ratio',title='Homogeneous iteration: gains');axs[1].legend(fontsize=8);axs[1].grid(alpha=.2)
 diff=r['direct_vs_iterated'];axs[2].bar([q['lead_months'] for q in diff],[100*q['relative_operator_frobenius'] for q in diff],color='#006e82');axs[2].set(xlabel='Published lead, months',ylabel='Operator difference / direct operator (%)',title='Direct maps versus one-step iteration');axs[2].grid(axis='y',alpha=.2)
 fig.suptitle('Frozen ctcal12 Floquet audit: annual eigen-radius %.6g, annual latent maximum gain %.6g' % (r['annual_spectral_radius'],r['annual_latent_operator_norm']),fontsize=13)
 fig.supxlabel('Annual product applies to the declared one-step homogeneous surrogate. Direct lead maps, forcing and real-weather skill remain separate.',fontsize=9)
 fig.savefig(out/'floquet-diagnostic.png',dpi=160);fig.savefig(out/'floquet-diagnostic.svg',metadata={'Date':None});plt.close(fig)
