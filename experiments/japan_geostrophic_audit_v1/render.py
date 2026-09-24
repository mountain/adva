"""Original static diagnostic figure; no map tiles or external graphics."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def render(out,contract):
 with np.load(out/'diagnostic-fields.npz',allow_pickle=False) as f:d={k:f[k] for k in f.files}
 plt.rcParams.update({'svg.fonttype':'none','font.size':9})
 fig,axes=plt.subplots(3,3,figsize=(16,12),layout='constrained')
 lat=d['lat'];lon=d['lon'];yi=np.where((lat>=20)&(lat<=60))[0];xi=np.where((lon>=120)&(lon<=200))[0]
 def crop(x):return x[yi][:,xi]
 def panel(ax,field,title,vmax,vectors=None,phi=None):
  im=ax.pcolormesh(lon[xi],lat[yi],crop(field),shading='nearest',cmap='viridis',vmin=0,vmax=vmax,rasterized=True)
  if phi is not None:
   height=crop(phi)/9.80665
   levels=np.arange(4800,6121,60) if np.nanmean(abs(height))>1000 else [-80,-40,-20,-10,-5,5,10,20,40,80]
   cs=ax.contour(lon[xi],lat[yi],height,levels=levels,colors='white',linewidths=.65,alpha=.85)
   ax.clabel(cs,inline=True,fontsize=6,fmt='%g')
  if vectors is not None:
   vv=crop(vectors)[::5,::5];q=ax.quiver(lon[xi][::5],lat[yi][::5],vv[:,:,0],vv[:,:,1],color='#202020',scale=650 if vmax>=20 else 70,width=.002)
   ax.quiverkey(q,.88,1.045,20 if vmax>=20 else 2,'20 m/s' if vmax>=20 else '2 m/s',labelpos='W',fontproperties={'size':7})
  ax.add_patch(Rectangle((140,25),40,20,fill=False,edgecolor='#ff7364',linestyle='--',lw=1.5))
  ax.set(xlim=(120,200),ylim=(20,60),title=title,xticks=[120,140,160,180,200],yticks=[20,30,40,50,60])
  ax.set_xticklabels(['120E','140E','160E','180','160W']);ax.set_ylabel('Latitude N');ax.grid(alpha=.14)
  fig.colorbar(im,ax=ax,shrink=.8,pad=.015,label='m/s',extend='max')
 v=d['forecast_wind'];b=d['baseline_wind'];p=d['forecast_phi'];bp=d['baseline_phi']
 for j,(vv,pp,title,vmax) in enumerate([(b,bp,'A  January effective climatology |Vbar|',60),(v,p,'B  Actual linked forecast: JANUARY 2026 |V|',60),(v-b,p-bp,'C  Learned anomaly |V - Vbar|',8)]):
  panel(axes[0,j],np.linalg.norm(vv,axis=-1),title,vmax,vv,pp)
 for j,(name,title,vmax) in enumerate([('baseline','D  Climatology |Vbar - G(Phi_bar)|',20),('total','E  January forecast |V - G(Phi)|',20),('anomaly','F  Learned anomaly |Vprime - G(Phi_prime)|',8)]):
  vv=d[name+'_residual'];panel(axes[1,j],np.linalg.norm(vv,axis=-1),title,vmax)
 panel(axes[2,0],np.linalg.norm(d['december_baseline_wind'],axis=-1),'G  December NATIVE climatology only',60,d['december_baseline_wind'],d['december_baseline_phi'])
 for ax,title in [(axes[2,1],'H  Requested December 2026 total'),(axes[2,2],'I  Requested December 2026 anomaly')]:
  ax.set_facecolor('#eeeeee');ax.set_xticks([]);ax.set_yticks([]);ax.set_title(title);ax.text(.5,.5,'UNAVAILABLE\n\nNo 2026-12 forecast in the frozen release.\nNo substitute month; no new extrapolation.',ha='center',va='center',transform=ax.transAxes,fontsize=11)
 fig.suptitle('Japan / western North Pacific 500 hPa physical review\nURL resolves to January 2026; requested December 2026 is absent',fontsize=16)
 fig.supxlabel('White contours: geopotential height (m); red box: 25-45N, 140-180E. Baseline: 1979-2014.\nA-F: published hybrid representation, unquantized grids. G: native December baseline interpolated only for plotting. No 2026 verification.',fontsize=10)
 fig.savefig(out/'combined-diagnostic.png',dpi=160);fig.savefig(out/'combined-diagnostic.svg',metadata={'Date':None});plt.close(fig)
