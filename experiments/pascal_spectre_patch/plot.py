#!/usr/bin/env python3
"""Render the retained rational patch, sphere image, and exact-check limits.

Original visualization by ChatGPT (OpenAI), contributed under Unknown v0.3
through Mingli Yuan's authorized account proxy. Display uses floating-point
sampling; all mathematical decisions belong to the separate exact checkers.
"""

import argparse
from fractions import Fraction
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

COLORS = ("#147D92", "#E99337", "#7664B0", "#4A9F78")
INK = "#183348"


def numeric_curves(vertices, epsilon, count=81):
    t = np.linspace(0, 1, count)[:, None]
    curves = []
    for i, a in enumerate(vertices):
        d = vertices[(i + 1) % len(vertices)] - a
        normal = np.array([-d[1], d[0]])
        curves.append(a + t * d + epsilon * t*t*(1-t)**2*(2*t-1) * normal)
    return curves


def spherical(xy):
    r2 = np.sum(xy * xy, axis=-1)
    return np.stack((2*xy[..., 0], 2*xy[..., 1], r2-1), axis=-1) / (1+r2)[..., None]


def subdivide_triangle(triangle, n=9):
    a, b, c = triangle
    def p(i, j):
        return a + (b-a)*i/n + (c-a)*j/n
    for i in range(n):
        for j in range(n-i):
            yield np.array([p(i, j), p(i+1, j), p(i, j+1)])
            if i+j < n-1:
                yield np.array([p(i+1, j), p(i+1, j+1), p(i, j+1)])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.report.read_text())
    if data.get("status") != "VerifiedLocalPatch":
        raise ValueError("plot requires a retained VerifiedLocalPatch report")
    if (data["input"]["sha256"] != "5d805463d69e0d5e2b248f09077e8a8bbaa09021938961c819383dae0960190c"
            or data["planar_patch"]["tile_count"] != 4
            or Fraction(data["curved_patch"]["epsilon"]) != Fraction(1, 100000)):
        raise ValueError("this annotated figure is pinned to the four-copy certified experiment")
    vertices = [np.array([[float(Fraction(c)) for c in p] for p in poly])
                for poly in data["planar_patch"]["vertices"]]
    epsilon = float(Fraction(data["curved_patch"]["epsilon"]))
    curves = [numeric_curves(poly, epsilon) for poly in vertices]
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.labelcolor": INK, "text.color": INK,
                         "axes.edgecolor": "#ACBBC4", "xtick.color": "#486171",
                         "ytick.color": "#486171", "savefig.facecolor": "white"})
    fig = plt.figure(figsize=(15.5, 11.2), facecolor="white")
    grid = fig.add_gridspec(2, 2, height_ratios=(1.5, 1), left=.085, right=.965,
                           bottom=.15, top=.84, wspace=.21, hspace=.36)
    fig.text(.06, .942, "Four curved tiles fit locally", fontsize=24, weight="bold")
    fig.text(.06, .907, "A sharp corner blocks a complete tiling; sphere projection preserves contacts, not congruence.",
             fontsize=13, color="#486171")
    ax = fig.add_subplot(grid[0, 0])
    ax.set_title("A   Exact planar patch: four congruent copies", loc="left", pad=16,
                 fontsize=13, weight="bold")
    for i, boundary in enumerate(curves):
        poly = np.concatenate(boundary)
        ax.add_patch(Polygon(poly, closed=True, facecolor=COLORS[i], alpha=.42,
                             edgecolor=COLORS[i], linewidth=1.4))
    for seam in data["planar_patch"]["shared_seams"]:
        tile, edge = seam[0]
        c = curves[tile][edge]
        ax.plot(c[:, 0], c[:, 1], color=INK, linewidth=2.7, zorder=5)
    p4 = vertices[0][4]
    ax.scatter(*p4, s=55, c="#B83D4B", marker="D", zorder=8,
               edgecolors="white", linewidths=.7)
    ax.annotate("$p_4$: unfillable corner", xy=p4, xytext=(-110, 31),
                textcoords="offset points", fontsize=10, color="#A32D3B",
                arrowprops={"arrowstyle": "-", "color": "#A32D3B", "lw": 1},
                bbox={"facecolor": "white", "alpha": .88, "edgecolor": "none", "pad": 2})
    all_vertices = np.concatenate(vertices)
    ax.set_xlim(all_vertices[:, 0].min()-.35, all_vertices[:, 0].max()+.35)
    ax.set_ylim(all_vertices[:, 1].min()-.35, all_vertices[:, 1].max()+.35)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=.15)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend([Line2D([], [], color=INK, lw=2.7), Line2D([], [], color="#B83D4B", marker="D", lw=0)],
              ["3 exactly shared curved seams", "Obstructing vertex"], frameon=False,
              loc="upper right", fontsize=9)
    ax.text(.02, .01, "Actual certified curvature\nNo visual exaggeration", transform=ax.transAxes,
            fontsize=9, color="#486171", va="bottom")

    sphere = fig.add_subplot(grid[0, 1], projection="3d")
    sphere.set_title("B   Inverse stereographic projection", loc="left", pad=16,
                     fontsize=13, weight="bold")
    lon = np.linspace(0, 2*np.pi, 37)
    lat = np.linspace(-np.pi/2, np.pi/2, 19)
    ll, pp = np.meshgrid(lon, lat)
    sphere.plot_wireframe(np.cos(pp)*np.cos(ll), np.cos(pp)*np.sin(ll), np.sin(pp),
                          color="#A6B8C3", linewidth=.45, alpha=.27, rstride=2, cstride=3)
    indices = data["triangulation"]
    for i, poly in enumerate(vertices):
        facets = [spherical(t) for ids in indices
                  for t in subdivide_triangle(poly[ids])]
        sphere.add_collection3d(Poly3DCollection(facets, facecolor=COLORS[i],
                                                edgecolor="none", alpha=.78))
        for c in curves[i]:
            xyz = spherical(c)
            sphere.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], color=COLORS[i], lw=1.25)
    for seam in data["planar_patch"]["shared_seams"]:
        tile, edge = seam[0]
        xyz = spherical(curves[tile][edge])
        sphere.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], color=INK, lw=2.1)
    sphere.set_box_aspect((1, 1, 1), zoom=1.2)
    sphere.set(xlim=(-1, 1), ylim=(-1, 1), zlim=(-1, 1))
    sphere.view_init(elev=26, azim=55)
    sphere.set_axis_off()
    sphere.text2D(.06, -.05, "$X^2+Y^2+Z^2=1$     Exact contacts, unequal spherical shapes",
                  transform=sphere.transAxes, fontsize=10, color="#486171")

    seam_ax = fig.add_subplot(grid[1, 0])
    seam_ax.set_title(r"C   Seam profile: normal displacement $\times\,100{,}000$", loc="left", pad=16,
                     fontsize=12.5, weight="bold")
    t = np.linspace(0, 1, 301)
    profile = epsilon*t*t*(1-t)**2*(2*t-1)
    seam_ax.fill_between(t, 0, profile*100000, color=COLORS[0], alpha=.16)
    seam_ax.plot(t, profile*100000, color=COLORS[0], lw=2.3)
    seam_ax.axhline(0, color="#8196A4", lw=.9, linestyle="--")
    seam_ax.scatter([0, 1], [0, 0], s=27, color=INK, zorder=3)
    seam_ax.set(xlim=(0, 1), ylim=(-.026, .026), xlabel="Fraction along the chord  t",
                ylabel="Normal offset / chord length\n(exaggerated 100,000 times)")
    seam_ax.grid(alpha=.15)
    seam_ax.spines[["top", "right"]].set_visible(False)
    seam_ax.text(.5, .94, "$\\varepsilon=10^{-5}$; endpoint tangents stay unchanged",
                 transform=seam_ax.transAxes, ha="center", va="top", fontsize=10)
    seam_ax.text(.5, -.27, r"Physical maximum offset: 1.78885 $\times\,10^{-7}$ of the edge length",
                 transform=seam_ax.transAxes, ha="center", fontsize=10, color="#486171")

    note = fig.add_subplot(grid[1, 1])
    note.set_axis_off()
    note.set_title("D   What the checks establish", loc="left", pad=16,
                   fontsize=13, weight="bold")
    note.text(.02, .91, "Local fit", fontsize=12, weight="bold", color=COLORS[0])
    note.text(.02, .79, "4 tiles  ·  3 seams  ·  1,378 exact hull-pair checks", fontsize=11)
    note.text(.02, .65, "Full tiling is blocked at $p_4$", fontsize=12, weight="bold", color="#A32D3B", va="top")
    note.text(.02, .53, "Unfilled wedge:  0.003091546°\nSmallest available tile corner:  0.256420136°",
              fontsize=11, linespacing=1.6, va="top")
    note.text(.02, .28, "Rational sphere image", fontsize=12, weight="bold", color=COLORS[0], va="top")
    note.text(.02, .16, "336 rational samples satisfy the sphere equation exactly.\nThe corner-to-corner chord multisets differ across copies.",
              fontsize=10.5, linespacing=1.5, va="top")
    fig.text(.06, .029, "Exact certificates: Fraction arithmetic. Rendering: numerical samples. No infinite tiling or aperiodicity is established.",
             color="#5D7280", fontsize=10)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=185)
    plt.close(fig)
    print(args.output)


if __name__ == "__main__":
    main()
