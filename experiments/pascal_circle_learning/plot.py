"""Plot an explicitly supplied seed and exact candidate; no embedded source art.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account proxy.
Original contribution under Unknown v0.3. Requires matplotlib and numpy.
The image is explanatory; check.py supplies the exact arithmetic verdict.
"""
from pathlib import Path
import argparse
import json
from fractions import Fraction
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

RED = '#d74442'
BLUE = '#2671bb'
GROUPS = {'red': [1, 3, 5, 7, 9], 'blue': [2, 4, 8, 12]}


def fit_circle(points):
    p = np.array(points[:3])
    center = np.linalg.solve(2 * (p[1:] - p[0]), (p[1:] ** 2).sum(1) - (p[0] ** 2).sum())
    return center, np.linalg.norm(p[0] - center)


def circle(ax, center, radius, color):
    ax.add_patch(Circle(center, radius, fill=False, edgecolor=color, lw=1.6, alpha=.85))


def draw_points(ax, p, indices, *, offsets=None):
    offsets = offsets or {}
    for i in indices:
        color = RED if i in GROUPS['red'] else BLUE if i in GROUPS['blue'] else '#313e4e'
        ax.scatter(*p[i], s=27, color=color, zorder=5)
        dx, dy = offsets.get(i, (5, 6))
        ax.annotate(str(i), p[i], xytext=(dx, dy), textcoords='offset points',
                    fontsize=10, color=color, weight='bold', zorder=6,
                    bbox={'facecolor':'white', 'alpha':.78, 'edgecolor':'none', 'pad':.3},
                    arrowprops={'arrowstyle':'-', 'lw':.4, 'color':color} if abs(dx)+abs(dy)>23 else None)


def infinite_line(ax, p, q, color, **kwargs):
    v = q - p
    ax.axline(p, p+v, color=color, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    seed = np.array(json.loads(args.seed.read_text())['points'], dtype=float)
    obj = json.loads(args.candidate.read_text())
    p = np.array([[float(Fraction(v)) for v in row] for row in obj['points']])
    cc = {n:(np.array([float(Fraction(x)) for x in c['center']]), np.sqrt(float(Fraction(c['radius_squared']))))
          for n,c in obj['circles'].items()}
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11})
    rms = np.sqrt(np.sum((p-seed)**2)/14)
    fig, axes = plt.subplots(2,2,figsize=(14,10), gridspec_kw={'height_ratios':[1.05,1]})
    fig.patch.set_facecolor('#fbfcfe')
    fig.suptitle('Tile(1,1) to an exact rational Pascal configuration', fontsize=20, weight='bold', y=.985)
    fig.text(.5,.947,'14 rational finite points  |  two exact Pascal bindings  |  blue center lies on red circle',ha='center',fontsize=11,color='#536175')
    for ax in axes.flat:
        ax.set_aspect('equal', adjustable='box')
        ax.set_facecolor('white')
        ax.spines[['top','right']].set_visible(False)
        ax.spines[['bottom','left']].set_color('#dce2eb')
        ax.tick_params(colors='#718097',labelsize=9)
        ax.grid(alpha=.1)
    ax=axes[0,0]
    ax.set_title('A   Original seed: circle memberships, failed bindings',loc='left',fontsize=12,pad=12)
    ax.plot(*np.vstack([seed,seed[0]]).T,color='#586578',lw=1.5)
    seed_cc = {}
    for n in GROUPS:
        c,r=fit_circle(seed[GROUPS[n]])
        seed_cc[n] = (c,r)
        circle(ax,c,r,RED if n=='red' else BLUE)
    for n in GROUPS:
        ax.scatter(*seed_cc[n][0], marker='+', s=70, color=RED if n=='red' else BLUE, zorder=6)
        ax.annotate('O5' if n=='red' else 'O4', seed_cc[n][0], xytext=(6,-15), textcoords='offset points', color=RED if n=='red' else BLUE, fontsize=9)
    ax.plot(*np.array([seed_cc['red'][0],seed_cc['blue'][0]]).T, color='#ac9c64', ls=':', lw=1.3)
    draw_points(ax,seed,range(14),offsets={3:(8,-12),4:(8,5),5:(8,5),9:(2,9),10:(-5,10),11:(-12,8),12:(-17,-5),1:(0,9),2:(0,-16)})
    # Point 10 is originally a fifth blue-circle point, but a straight vertex.
    ax.scatter(*seed[10],s=90,facecolors='none',edgecolors=BLUE,lw=1.5,zorder=4)
    ax.plot(*seed[[0,6,10]].T,color=BLUE,ls='--',lw=1,alpha=.6)
    ax.set_xlim(-1.4,4.4);ax.set_ylim(-1.2,3.6)
    ax.text(.02,.02,'0, 6, 10 are not collinear; 10 also lies on the blue circle.',transform=ax.transAxes,fontsize=9,color='#536175')
    ax=axes[0,1]
    ax.set_title('B   Learned rational result: all exact checks pass',loc='left',fontsize=12,pad=12)
    ax.plot(*np.vstack([p,p[0]]).T,color='#586578',lw=1.6)
    for n,(c,r) in cc.items():circle(ax,c,r,RED if n=='red' else BLUE)
    draw_points(ax,p,[0,2,4,6,8,10,11,12,13],offsets={0:(8,5),2:(9,-10),4:(8,4),8:(-18,5),10:(-12,-16),11:(-20,7),12:(-12,-14),13:(-18,-4)})
    for i in GROUPS['red']:ax.scatter(*p[i],s=22,color=RED,zorder=5)
    ax.text(.03,.88,'Red circle detail: panel D', transform=ax.transAxes, fontsize=10,color=RED)
    infinite_line(ax,p[0],p[6],BLUE,ls='--',lw=1.1,alpha=.7)
    infinite_line(ax,p[11],p[13],RED,ls='--',lw=1.1,alpha=.7)
    ax.set_xlim(-1.4,4.4);ax.set_ylim(-1.2,3.6)
    for n in GROUPS:
        ax.scatter(*cc[n][0], marker='+', s=70, color=RED if n=='red' else BLUE, zorder=6)
        ax.annotate('O5' if n=='red' else 'O4', cc[n][0], xytext=(6,-15), textcoords='offset points', color=RED if n=='red' else BLUE, fontsize=9)
    ax.plot(*np.array([cc['red'][0],cc['blue'][0]]).T, color='#ac9c64', ls=':', lw=1.3)
    ax.text(.02,.02,f'Same axes as A. RMS displacement = {rms:.5f} seed edge lengths.',transform=ax.transAxes,fontsize=9,color='#536175')
    ax=axes[1,0]
    ax.set_title('C   Blue: two tangencies, three finite Pascal points',loc='left',fontsize=12,pad=12)
    circle(ax,*cc['blue'],BLUE)
    for a,b in [(2,4),(8,12),(4,8),(12,2)]:infinite_line(ax,p[a],p[b],'#9aa6b5',lw=.9,alpha=.65)
    for a in [2,8]:infinite_line(ax,p[a],p[a]+np.array([-(p[a]-cc['blue'][0])[1],(p[a]-cc['blue'][0])[0]]),'#9aa6b5',lw=.9,alpha=.65)
    infinite_line(ax,p[0],p[6],BLUE,ls='--',lw=1.7)
    draw_points(ax,p,[0,2,4,6,8,10,12],offsets={0:(5,9),2:(8,-14),4:(10,5),8:(-17,8),10:(-16,-16),12:(-16,-10),6:(7,8)})
    ax.set_xlim(-.7,4.4);ax.set_ylim(-.15,3.15)
    ax.text(.02,.02,'Pascal line through 0, 6, 10; grey lines are chords and tangents.',transform=ax.transAxes,fontsize=9,color=BLUE)
    ax=axes[1,1]
    ax.set_title('D   Red circle detail: one tangency, one infinity point',loc='left',fontsize=12,pad=12)
    circle(ax,*cc['red'],RED)
    for a,b in [(1,3),(7,9)]:infinite_line(ax,p[a],p[b],RED,ls='--',lw=1.1,alpha=.7)
    for a,b in [(3,5),(9,1),(5,7)]:infinite_line(ax,p[a],p[b],'#9aa6b5',lw=.8,alpha=.6)
    a=1;infinite_line(ax,p[a],p[a]+np.array([-(p[a]-cc['red'][0])[1],(p[a]-cc['red'][0])[0]]),'#9aa6b5',lw=.8,alpha=.6)
    ax.scatter(*cc['blue'][0], marker='+', s=90, color=BLUE, zorder=6)
    ax.annotate('O4',cc['blue'][0],xytext=(8,8),textcoords='offset points',color=BLUE,weight='bold')
    draw_points(ax,p,GROUPS['red'],offsets={1:(8,6),3:(-26,0),5:(-13,-20),7:(7,12),9:(-28,15)})
    c,r=cc['red'];ax.set_xlim(c[0]-1.55*r,c[0]+1.65*r);ax.set_ylim(c[1]-1.5*r,c[1]+1.8*r)
    ax.text(.02,.02,'chord(1,3) ∥ chord(7,9); Pascal line: 11, 13, infinity.',transform=ax.transAxes,fontsize=9,color=RED)
    fig.text(.03,.018,'The shape changes substantially; tiling and aperiodicity are not asserted. Exact rational arithmetic, not this drawing, verifies incidence.',fontsize=10,color='#536175')
    fig.subplots_adjust(left=.05,right=.975,top=.905,bottom=.075,hspace=.25,wspace=.16)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(args.output,dpi=160,facecolor=fig.get_facecolor())


if __name__=='__main__':main()
