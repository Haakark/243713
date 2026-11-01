# -*- coding: utf-8 -*-
"""官方 nichenetr 重做版 PPT（14 页）。"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

BASE = r"C:\Users\lenovo\Desktop\nichenet_data"
AGG = os.path.join(BASE, "official_nichenet_results", "20261101_2125")
PRI = os.path.join(BASE, "official_prioritization")
OUT = os.path.join(BASE, "NicheNet_official_redo_report.pptx")

NAVY = RGBColor(0x1B, 0x2A, 0x5B); BLUE = RGBColor(0x2C, 0x7F, 0xB8)
LIGHTBLUE = RGBColor(0x6B, 0xAE, 0xD6); RED = RGBColor(0xA5, 0x0F, 0x15)
SALMON = RGBColor(0xFC, 0x92, 0x72); GREEN = RGBColor(0x00, 0x6D, 0x2C)
GREY = RGBColor(0x59, 0x59, 0x59); DARK = RGBColor(0x33, 0x33, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF); PALE = RGBColor(0xF2, 0xF4, 0xF8)
FONT = "微软雅黑"; SW, SH = 13.333, 7.5


def sf(run, size=None, bold=None, color=None, italic=None):
    run.font.name = FONT
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {}); rPr.append(ea)
    ea.set("typeface", FONT)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color is not None: run.font.color.rgb = color


def tb(s, l, t, w, h, text, size=14, bold=False, color=DARK, align=PP_ALIGN.LEFT,
       anchor=MSO_ANCHOR.TOP, ls=1.15, italic=False):
    box = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.02))
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = ls
        r = p.add_run(); r.text = line
        sf(r, size=size, bold=bold, color=color, italic=italic)


def slide(prs): return prs.slides.add_slide(prs.slide_layouts[6])


def header(s, title, sub=None):
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(0.13))
    bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    tb(s, 0.55, 0.30, 12.2, 0.55, title, size=25, bold=True, color=NAVY)
    if sub:
        tb(s, 0.57, 0.86, 12.2, 0.34, sub, size=11.5, color=GREY)
    ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.18), Inches(12.2), Pt(1.2))
    ln.fill.solid(); ln.fill.fore_color.rgb = LIGHTBLUE; ln.line.fill.background()


def footer(s, page, total=14):
    tb(s, 0.55, 7.10, 8.5, 0.28, "官方 nichenetr 重做 · 7 个小胶质细胞亚型 · AD vs No Neuropathology",
       size=8.5, color=GREY)
    tb(s, 11.6, 7.10, 1.2, 0.28, f"{page} / {total}", size=8.5, color=GREY, align=PP_ALIGN.RIGHT)


def pic(s, path, l, t, w, h):
    with Image.open(path) as im:
        iw, ih = im.size
    r = iw / ih
    if w / h > r: hh = h; ww = hh * r
    else: ww = w; hh = ww / r
    s.shapes.add_picture(path, Inches(l + (w - ww) / 2), Inches(t + (h - hh) / 2),
                         Inches(ww), Inches(hh))


def bullets(s, items, l, t, w, h, size=12):
    box = s.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    for i, it in enumerate(items):
        text, lvl = it if isinstance(it, tuple) else (it, 0)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = lvl; p.space_after = Pt(6); p.line_spacing = 1.22
        r0 = p.add_run(); r0.text = "▪ " if lvl == 0 else "– "; sf(r0, size=size, color=NAVY)
        r1 = p.add_run(); r1.text = text; sf(r1, size=size - (1 if lvl else 0), color=DARK)


def callout(s, l, t, w, h, text, size=11, color=NAVY):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    box.fill.solid(); box.fill.fore_color.rgb = PALE
    box.line.color.rgb = LIGHTBLUE; box.line.width = Pt(1)
    tf = box.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.12); tf.margin_right = Inches(0.12)
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        r = p.add_run(); r.text = line; sf(r, size=size, bold=True, color=color)


def table(s, rows, l, t, w, h, widths, size=10):
    tbl = s.shapes.add_table(len(rows), len(rows[0]), Inches(l), Inches(t), Inches(w), Inches(h)).table
    for i, cw in enumerate(widths): tbl.columns[i].width = Inches(cw)
    for r in range(len(rows)):
        for c in range(len(rows[0])):
            cell = tbl.cell(r, c); cell.text = ""
            cell.margin_left = Inches(0.05); cell.margin_right = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
            run = p.add_run(); run.text = str(rows[r][c])
            if r == 0:
                sf(run, size=size, bold=True, color=WHITE)
                cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            else:
                sf(run, size=size, bold=(c == 0), color=DARK)
                cell.fill.solid(); cell.fill.fore_color.rgb = PALE if r % 2 == 0 else WHITE


def notes(s, text): s.notes_slide.notes_text_frame.text = text


prs = Presentation(); prs.slide_width = Inches(SW); prs.slide_height = Inches(SH)

# 1 cover
s = slide(prs)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(SH))
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
tb(s, 1.0, 2.1, 11.3, 0.4, "基于 saeyslab/nichenetr 官方代码", size=18, color=LIGHTBLUE)
tb(s, 1.0, 2.55, 11.4, 1.0, "AD 小胶质细胞 7 亚型通讯：官方流程重做", size=34, bold=True, color=WHITE)
tb(s, 1.0, 3.70, 11.3, 0.5, "nichenet_seuratobj_aggregate ｜ AUPR 排序 ｜ 表达量优先级 ｜ Circos 与 Mushroom",
   size=13, color=RGBColor(0xD0, 0xD8, 0xEA))
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.35), Inches(2.6), Pt(2.5))
ln.fill.solid(); ln.fill.fore_color.rgb = SALMON; ln.line.fill.background()
tb(s, 1.0, 4.65, 11.3, 1.0,
   "7 个 receiver × (AD vs No Neuropathology)\n结果：official_nichenet_results/20261101_2125 ｜ official_prioritization/",
   size=11.5, color=RGBColor(0xC8, 0xD2, 0xE6))
tb(s, 1.0, 6.55, 11.3, 0.35, "2026-11-01", size=10.5, color=RGBColor(0x9F, 0xAE, 0xCC))
notes(s, "上一版是我们自己写的流程（Pearson + 方向性基因集）。这一版改用 Saeyslab 官方 wrapper 与可视化函数重跑，重点讲差异。")

# 2 why
s = slide(prs); header(s, "为什么重做", "用官方代码复现，检查结论是否依赖实现细节")
bullets(s, [
    "上一版：自写流程，配体按 Pearson 排序，上调/下调各取 top200 基因集",
    "这一版：官方 nichenet_seuratobj_aggregate()，按 AUPR 排序，基因集用全部 DE 基因",
    "另外补上官方独有的两件事：表达量优先级（circos + mushroom）与官方组合图",
    "目的：看哪些结论在两种实现下都成立，哪些只是实现差异",
], 0.65, 1.45, 12.0, 3.2, size=13)
callout(s, 0.65, 4.9, 12.1, 1.2,
        "结论先说：TGFB1（下调方向）在两种实现、两种指标下都成立；\nLY86（上调第一）只在 Pearson 下成立，AUPR 下被 NLGN4Y/NLGN1 取代。")
footer(s, 2); notes(s, "重做的目的不是推翻，而是做敏感性检查：看结论是否稳健。")

# 3 workflow
s = slide(prs); header(s, "官方工作流：一个函数完成五步", "nichenet_seuratobj_aggregate 内部依次完成")
steps = [("① 潜在配体", "配体在 sender 表达\n且受体在 receiver 表达"),
         ("② 基因集", "receiver 内 AD vs 对照\n全部 DE 基因"),
         ("③ 背景基因", "receiver 全部表达基因"),
         ("④ 配体活性", "predict_ligand_activities\nAUPR 排序"),
         ("⑤ 下游", "靶基因、受体、\nLFC 热图、组合图")]
x = 0.62
for i, (t, d) in enumerate(steps):
    b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.9), Inches(2.2), Inches(2.2))
    b.fill.solid(); b.fill.fore_color.rgb = PALE; b.line.color.rgb = LIGHTBLUE
    tb(s, x + 0.1, 2.05, 2.0, 0.4, t, size=13, bold=True, color=NAVY, align=PP_ALIGN.CENTER)
    tb(s, x + 0.1, 2.55, 2.0, 1.4, d, size=9.5, color=DARK, align=PP_ALIGN.CENTER)
    if i < 4:
        a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.26), Inches(2.8), Inches(0.28), Inches(0.4))
        a.fill.solid(); a.fill.fore_color.rgb = LIGHTBLUE; a.line.fill.background()
    x += 2.54
tb(s, 0.62, 4.45, 12.0, 1.4,
   "官方还提供两个扩展：generate_info_tables() + generate_prioritization_tables()（表达量优先级），"
   "以及 make_circos_lr() / make_mushroom_plot() 可视化。我们用这三位一体补做了 3 个 receiver。",
   size=11, color=GREY)
footer(s, 3); notes(s, "官方把五步封装成一个函数；优先级和 circos/mushroom 是额外的官方扩展。")

# 4 params
s = slide(prs); header(s, "数据与参数", "为了让官方 DE 跑得动，先把对象精简到 4,854 个表达基因")
rows = [["项目", "设置"],
        ["数据", "scRNA（7 亚型，38,664 cells）→ slim 对象 4,854 genes"],
        ["分组", "group_use：AD vs No Neuropathology"],
        ["sender", "all（7 个亚群，含自分泌）"],
        ["expression_pct", "0.10"],
        ["lfc_cutoff", "0.25（padj ≤ 0.05）"],
        ["geneset", "DE（上调+下调全部）"],
        ["top_n_ligands", "30"],
        ["网络", "lr_network 21122021 / ligand_target nsga2r / weighted_networks"]]
table(s, rows, 0.7, 1.5, 11.9, 4.4, [3.2, 8.7], size=10.5)
callout(s, 0.7, 6.15, 11.9, 0.65, "7 个 receiver 全部跑通，总耗时 24.9 分钟。")
footer(s, 4); notes(s, "slim 对象只删掉从不表达的基因，不改变 DE/背景的可检测范围。")

# 5 results table
s = slide(prs); header(s, "官方结果总览", "AUPR 排序，基因集为全部 DE 基因")
rows = [["receiver", "DE 基因数", "top1", "top5"],
        ["Homeos1", "2,038", "TGFB1", "TGFB1, HMGB1, NLGN1, PSAP, TSPAN3"],
        ["Homeos2", "1,023", "TGFB1", "TGFB1, PSAP, LIPC, ENG, GAS6"],
        ["Homeos3", "197", "NLGN1", "NLGN1, TGFB1, JAM2, CXCL12, IL1B"],
        ["Inflam.DAM", "2,866", "HMGB1", "HMGB1, PSAP, TGFB1, PTPRM, NLGN1"],
        ["Lipo.DAM", "1,393", "HMGB1", "HMGB1, PSAP, TGFB1, NLGN1, GAS6"],
        ["Ribo.DAM1", "1,589", "TGFB1", "TGFB1, JAM2, HMGB1, PSAP, IL18"],
        ["Ribo.DAM2", "642", "PSAP", "PSAP, NRXN3, CALR, HMGB1, TSPAN3"]]
table(s, rows, 0.6, 1.45, 12.2, 4.3, [1.7, 1.6, 1.5, 7.4], size=10)
tb(s, 0.6, 6.0, 12.1, 0.8,
   "TGFB1 出现在 5/7 个亚型的 top3；HMGB1、PSAP 也反复出现——这三个都是“下调方向”的配体。",
   size=10.5, color=GREY)
footer(s, 5); notes(s, "官方结果里 TGFB1/HMGB1/PSAP 反复出现，与上调方向的 LY86 形成对比。")

# 6 dotplot
s = slide(prs); header(s, "配体在 7 个亚型中的表达", "官方图：ligand_expression_dotplot（Homeos1 的 top 配体）")
pic(s, os.path.join(AGG, "receiver_Homeos1", "05_ligand_expression_dotplot.png"), 0.6, 1.35, 7.4, 5.6)
bullets(s, [
    "TGFB1、APOE 在 7 个亚型中广泛表达，属于“普遍信号”",
    "HMGB1 在 Ribo.DAM1 最高，PSAP 在 Lipo.DAM / Ribo.DAM2 最高",
    "PSAP、APOE 的高表达与其在优先级表中的高排名一致",
], 8.2, 1.6, 4.6, 4.6, size=11)
footer(s, 6); notes(s, "官方 dotplot：行是配体，列是 sender 亚型，颜色是平均表达、大小是检出比例。")

# 7 LFC heatmap
s = slide(prs); header(s, "配体在 sender 中的 AD vs 对照 LFC", "官方图：ligand_differential_expression_heatmap（三色）")
pic(s, os.path.join(AGG, "receiver_Homeos1", "02_ligand_lfc_sender_threecolor.png"), 0.7, 1.4, 6.4, 5.5)
bullets(s, [
    "TGFB1 在多数亚型中下调，与其“下调方向配体”的身份一致",
    "HMGB1、PSAP 在部分亚型上调",
    "这张图只是附加证据，不参与排序（官方说明）",
], 7.4, 1.7, 5.3, 4.4, size=11.5)
footer(s, 7); notes(s, "官方明确说 LFC 不参与排序，只作为额外证据。")

# 8 LR heatmap
s = slide(prs); header(s, "配体–受体关系", "官方图：ligand_receptor_heatmap（Homeos1）")
pic(s, os.path.join(AGG, "receiver_Homeos1", "04_ligand_receptor_heatmap.png"), 0.8, 1.4, 6.2, 5.5)
bullets(s, [
    "TGFB1 的受体：TGFBR1/2、ENG、ITGB1、ITGAV",
    "APOE 的受体：LRP1、TREM2、SCARB1、SORL1",
    "PSAP 的受体：LRP1；HMGB1 的受体：HAVCR2",
    "官方只保留在 receiver 中表达的受体",
], 7.3, 1.7, 5.4, 4.4, size=11.5)
footer(s, 8); notes(s, "配体-受体热图展示官方优先级下的受体推断。")

# 9 mushroom
s = slide(prs); header(s, "官方表达量优先级：Mushroom plot", "make_mushroom_plot（Homeos1，top30 配体-受体对）")
pic(s, os.path.join(PRI, "receiver_Homeos1", "02_mushroom_top30.png"), 0.55, 1.35, 6.9, 5.6)
bullets(s, [
    "每个蘑菇 = 一个配体-受体对；左右半圆分别代表配体/受体的表达与 p 值",
    "数字是优先级排名：TGFB1–ITGB1（第 3）、TGFB1–ENG（第 6/8/9/11）排在最前",
    "HLA-C/HLA-B–LILRB1、APOE–TREM2、APOE–LRP1 进入前 30",
    "比单纯配体活性多了“表达特异性 + 条件特异性”的维度",
], 7.55, 1.55, 5.2, 4.9, size=10.5)
footer(s, 9); notes(s, "Mushroom plot 是官方优先级流程的核心图，把配体/受体的表达和条件差异放在一起。")

# 10 circos
s = slide(prs); header(s, "官方 Circos：配体-受体全景", "make_circos_lr（Homeos1，top50 配体-受体对）")
pic(s, os.path.join(PRI, "receiver_Homeos1", "01_circos_top50.png"), 0.7, 1.35, 6.4, 5.6)
bullets(s, [
    "扇区按 sender 亚型着色：配体一侧是 7 个亚型，受体一侧是 Homeos1",
    "TGFB1 的连线最粗，来自多个 sender 亚型",
    "HLA 家族–LILRB1、APOE–TREM2/LRP1、PSAP–LRP1 构成主要网络",
    "注意：官方函数在 png 上会只剩图例，需用 pdf 输出第 1 页再转图（已在脚本中处理）",
], 7.35, 1.55, 5.4, 4.9, size=10.5)
footer(s, 10); notes(s, "circos 用官方 make_circos_lr；它有多页输出问题，脚本里用 pdf 第 1 页转 png。")

# 11 lipo mushroom
s = slide(prs); header(s, "另一个 receiver：Lipo.DAM 的优先级", "同一套流程，换 receiver 后优先级明显不同")
pic(s, os.path.join(PRI, "receiver_Lipo.DAM", "02_mushroom_top30.png"), 0.55, 1.35, 6.6, 5.6)
bullets(s, [
    "Lipo.DAM 的 top 对以 HLA–LILRB1、APOE–TREM2/LRP1、PSAP–LRP1 为主",
    "TGFB1 仍然靠前，但其受体组合与 Homeos1 不同",
    "说明优先级不仅取决于配体活性，还取决于该亚型自身的受体表达",
], 7.3, 1.6, 5.4, 4.6, size=11.5)
footer(s, 11); notes(s, "换一个 receiver，mushroom 的排名会变，体现受体侧的特异性。")

# 12 method comparison
s = slide(prs); header(s, "方法学对比：官方 vs 上一版", "同一批数据，两种实现")
rows = [["环节", "官方 wrapper", "上一版（自写）"],
        ["基因集", "全部 DE（含上下调）", "上调/下调各 top200"],
        ["排序指标", "AUPR（aupr_corrected）", "Pearson"],
        ["候选配体", "配体表达 + 受体表达", "仅配体表达"],
        ["额外输出", "mushroom/circos/组合图", "circos/LFC/信号通路"],
        ["Homeos1 top1", "TGFB1", "LY86（上调）/ TGFB1（下调）"]]
table(s, rows, 0.7, 1.5, 11.9, 3.6, [2.4, 4.7, 4.8], size=10.5)
callout(s, 0.7, 5.5, 11.9, 1.1,
        "差异主要来自“基因集是否分方向”和“AUPR vs Pearson”，不是数据本身。\n"
        "因此两条结论要分开表述：TGFB1 稳健；LY86 依赖指标。")
footer(s, 12); notes(s, "把差异归因到方法，而不是数据，避免误读。")

# 13 AUPR baseline
s = slide(prs); header(s, "关键问题：全部 DE 基因做 gene set，AUPR 基线过高", "以 Homeos1 为例")
rows = [["指标", "数值"],
        ["DE 基因数", "2,038"],
        ["背景基因数", "3,475"],
        ["DE 占背景比例", "53.4%"],
        ["AUPR 随机基线", "≈ 0.53"],
        ["aupr_corrected 范围", "−0.021 ~ +0.015"],
        ["top1 vs top2 差距", "0.0153 vs 0.0087"]]
table(s, rows, 0.7, 1.5, 6.2, 3.9, [3.0, 3.2], size=10.5)
bullets(s, [
    "当一半以上的表达基因都是 DE 时，AUPR 的“随机水平”就是 0.5 左右",
    "此时 aupr_corrected 只剩千分位差异，排序对抽样很敏感",
    "这不是官方的错，而是 gene set 定义不适合本数据",
    "建议：按方向拆基因集，或限制 top200",
], 7.3, 1.55, 5.4, 4.6, size=11)
footer(s, 13); notes(s, "这是本次重做最重要的方法学发现：DE 比例过高时 AUPR 失效。")

# 14 directional AUPR + conclusions
s = slide(prs); header(s, "方向性基因集的 AUPR：结论分层", "官方 predict_ligand_activities + 方向性 top200")
rows = [["receiver", "上调 top3（AUPR）", "下调 top3（AUPR）"],
        ["Homeos1", "NLGN4Y, NRXN1, NLGN1", "TGFB1, HLA-DQA2, CALR"],
        ["Homeos2", "IL18, IL1B, TIMP1", "TGFB1, IL1B, HMGB1"],
        ["Inflam.DAM", "NLGN4Y, NLGN1, NRXN3", "TGFB1, ENG, HMGB1"],
        ["Lipo.DAM", "NLGN1, NLGN4Y, LRP1B", "ENG, TGFB1, APOE"],
        ["Ribo.DAM1", "IL18, NLGN1, NLGN4Y", "TGFB1, PTPRM, HMGB1"],
        ["Ribo.DAM2", "LRP1B, CALR, NRXN3", "PSAP, HMGB1, TGFB1"]]
table(s, rows, 0.6, 1.4, 12.2, 3.3, [1.7, 5.0, 5.5], size=9.5)
callout(s, 0.6, 5.0, 12.2, 1.0,
        "稳健结论：TGFB1 下调（Pearson 与 AUPR 一致，6–7 个亚型）。\n"
        "条件性结论：LY86 上调第一仅在 Pearson 下成立；AUPR 下是 NLGN4Y/NLGN1（可能为环境 RNA）。", size=10.5)
tb(s, 0.6, 6.2, 12.2, 0.7,
   "建议：主图用方向性基因集 + AUPR；官方 wrapper（combined DE）作为补充与敏感性分析。",
   size=10.5, bold=True, color=RED)
footer(s, 14); notes(s, "最后给出结论分层和写作建议。")

prs.save(OUT)
print("saved", OUT, len(prs.slides))
