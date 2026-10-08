"""Plot chapter 2 attention evidence in grayscale; never synthesize matrix values."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.font_manager import FontProperties, fontManager

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'chapter2/attention_visualization/runs/exp2-2-qwen3-0.6b-20260730-v3'
FONT_PATH = ROOT / 'book/fonts/SourceHanSansCN-Regular.otf'
fontManager.addfont(str(FONT_PATH))
FONT = FontProperties(fname=str(FONT_PATH))
plt.rcParams.update({'font.family': FONT.get_name(), 'font.size': 12, 'axes.unicode_minus': False})

def main():
    matrices = np.load(RUN / 'attention_matrices.npz')
    evidence = json.loads((RUN / 'evidence.json').read_text())
    thinking = min(evidence['generated']['regions']['thinking'])
    answer = min(evidence['generated']['regions']['answer'])
    fig, axes = plt.subplots(3, 2, figsize=(5.3, 9.3))
    fig.subplots_adjust(left=.14, right=.96, top=.96, bottom=.21, wspace=.62, hspace=.65)
    cmap = plt.get_cmap('Greys').copy()
    cmap.set_bad('white')
    for row, layer in enumerate([0, 13, 27]):
        for col, kind in enumerate(['simple', 'generated']):
            ax = axes[row,col]
            data = matrices[f'{kind}_layer_{layer}']
            im = ax.imshow(np.ma.masked_less_equal(data, 0), cmap=cmap,
                           norm=LogNorm(vmin=1e-4, vmax=1), interpolation='nearest', rasterized=True)
            ax.set_title(f'{"短句" if col == 0 else "推理与回答"} · 第 {layer} 层', fontsize=13)
            ax.set_xlabel('Key 位置', fontsize=12)
            ax.set_ylabel('Query 位置', fontsize=12)
            ticks = [0,4,8] if col == 0 else [0,200,400,579]
            ax.set_xticks(ticks);ax.set_yticks(ticks)
            ax.tick_params(labelsize=11)
            if col:
                for boundary, style in [(thinking, '--'), (answer, ':')]:
                    ax.axhline(boundary-.5, color='#777777', linestyle=style, linewidth=.65)
                    ax.axvline(boundary-.5, color='#777777', linestyle=style, linewidth=.65)
    cax=fig.add_axes([.20,.12,.60,.016])
    cb=fig.colorbar(im,cax=cax,orientation='horizontal',ticks=[1e-4,1e-3,1e-2,1e-1,1])
    cb.set_ticklabels(['0.0001','0.001','0.01','0.1','1'])
    cb.ax.minorticks_off()
    cb.set_label('注意力权重（对数灰度）',fontsize=12)
    region_legend = fig.text(.5, .027, '输入：0–47　推理：48–565　回答：566–579',
             ha='center', fontsize=11)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    assert not cb.ax.xaxis.label.get_window_extent(renderer).overlaps(
        region_legend.get_window_extent(renderer)), 'Color scale and region legend overlap'
    for row in range(2):
        for col in range(2):
            assert not axes[row, col].xaxis.label.get_window_extent(renderer).overlaps(
                axes[row+1, col].title.get_window_extent(renderer)), 'Adjacent panel labels overlap'
    fig.savefig(ROOT/'book/images/fig2-7.png',dpi=400,facecolor='white',bbox_inches='tight',pad_inches=.04)
    plt.close(fig)

if __name__ == '__main__':
    main()
