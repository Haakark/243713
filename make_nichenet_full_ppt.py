# -*- coding: utf-8 -*-
"""Merged deck: analysis report text + figures, Chinese, 16:9."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

BASE = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                    "NicheNet_results_7subtypes", "20261031_1842")
OUT = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                   "NicheNet_7subtypes_AD_full_report.pptx")

NAVY = RGBColor(0x1B, 0x2A, 0x5B)
BLUE = RGBColor(0x2C, 0x7F, 0xB8)
LIGHTBLUE = RGBColor(0x6B, 0xAE, 0xD6)
RED = RGBColor(0xA5, 0x0F, 0x15)
SALMON = RGBColor(0xFC, 0x92, 0x72)
GREEN = RGBColor(0x00, 0x6D, 0x2C)
LIGHTGREEN = RGBColor(0xA1, 0xD9, 0x9B)
GREY = RGBColor(0x59, 0x59, 0x59)
DARKGREY = RGBColor(0x33, 0x33, 0x33)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE = RGBColor(0xF2, 0xF4, 0xF8)
FONT = "微软雅黑"
SW, SH = 13.333, 7.5


def set_run_font(run, size=None, bold=None, color=None, name=FONT, italic=None):
    run.font.name = name
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = rPr.makeelement(qn("a:ea"), {})
        rPr.append(ea)
    ea.set("typeface", name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def textbox(slide, left, top, width, height, text, size=14, bold=False,
            color=DARKGREY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
            line_spacing=1.15, italic=False):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, Inches(0.02))
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        set_run_font(run, size=size, bold=bold, color=color, italic=italic)
    return box


def add_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def header(slide, title, sub=None):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(0.13))
    bar.fill.solid(); bar.fill.fore_color.rgb = NAVY; bar.line.fill.background()
    textbox(slide, 0.55, 0.30, 12.2, 0.55, title, size=26, bold=True, color=NAVY)
    if sub:
        textbox(slide, 0.57, 0.86, 12.2, 0.34, sub, size=12, color=GREY)
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.55), Inches(1.18),
                                  Inches(12.2), Pt(1.2))
    line.fill.solid(); line.fill.fore_color.rgb = LIGHTBLUE; line.line.fill.background()


def footer(slide, page, total):
    textbox(slide, 0.55, 7.10, 8.0, 0.28,
            "NicheNet · 7 个小胶质细胞亚型 · AD vs No Neuropathology", size=9, color=GREY)
    textbox(slide, 11.6, 7.10, 1.2, 0.28, f"{page} / {total}", size=9, color=GREY,
            align=PP_ALIGN.RIGHT)


def image_fit(slide, path, left, top, width, height):
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = iw / ih
    if width / height > ratio:
        h = height; w = h * ratio
    else:
        w = width; h = w / ratio
    l = left + (width - w) / 2
    t = top + (height - h) / 2
    slide.shapes.add_picture(path, Inches(l), Inches(t), Inches(w), Inches(h))


def bullets(slide, items, left, top, width, height, size=12.5, color=DARKGREY):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        text, level = (item if isinstance(item, tuple) else (item, 0))
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = level
        p.space_after = Pt(7)
        p.line_spacing = 1.25
        r0 = p.add_run(); r0.text = "▪ " if level == 0 else "– "
        set_run_font(r0, size=size, color=NAVY)
        r1 = p.add_run(); r1.text = text
        set_run_font(r1, size=size - (1.5 if level else 0), color=color)
    return box


def callout(slide, left, top, width, height, text, color=NAVY, size=11, fill=PALE):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top),
                                 Inches(width), Inches(height))
    box.fill.solid(); box.fill.fore_color.rgb = fill
    box.line.color.rgb = LIGHTBLUE; box.line.width = Pt(1)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.12); tf.margin_right = Inches(0.12)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, line in enumerate(text.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run(); run.text = line
        set_run_font(run, size=size, bold=True, color=color)


def table(slide, rows, left, top, width, height, col_widths, font_size=10.5):
    tbl = slide.shapes.add_table(len(rows), len(rows[0]), Inches(left), Inches(top),
                                 Inches(width), Inches(height)).table
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = Inches(w)
    for r in range(len(rows)):
        for c in range(len(rows[0])):
            cell = tbl.cell(r, c)
            cell.text = ""
            cell.margin_left = Inches(0.06); cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.02); cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c > 0 else PP_ALIGN.LEFT
            run = p.add_run(); run.text = str(rows[r][c])
            if r == 0:
                set_run_font(run, size=font_size, bold=True, color=WHITE)
                cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
            else:
                set_run_font(run, size=font_size, bold=(c == 0), color=DARKGREY)
                cell.fill.solid()
                cell.fill.fore_color.rgb = PALE if r % 2 == 0 else WHITE
    return tbl


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


TOTAL = 24
prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)

# 1 ---------------------------------------------------------------- cover
s = add_slide(prs)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(SH))
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
textbox(s, 1.0, 1.95, 11.3, 0.4, "AD 脑内小胶质细胞亚型间通讯", size=18, color=LIGHTBLUE)
textbox(s, 1.0, 2.40, 11.4, 1.2,
        "NicheNet 配体–靶基因–受体–信号通路分析", size=34, bold=True, color=WHITE)
textbox(s, 1.0, 3.60, 11.3, 0.5,
        "7 个亚型 × (AD vs No Neuropathology)｜每个亚型各做一次 receiver",
        size=14, color=RGBColor(0xD0, 0xD8, 0xEA))
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.30),
                          Inches(2.6), Pt(2.5))
line.fill.solid(); line.fill.fore_color.rgb = SALMON; line.line.fill.background()
textbox(s, 1.0, 4.60, 11.3, 1.0,
        "数据：scRNA.RData（48,347 cells；去除 DIMs / MAC 后 38,664 cells / 7 亚群）\n"
        "结果：NicheNet_results_7subtypes/20261031_1842（275 个文件）",
        size=11.5, color=RGBColor(0xC8, 0xD2, 0xE6))
textbox(s, 1.0, 6.55, 11.3, 0.35, "完整汇报版（方法 + 结果 + 解读 + 局限）｜2026-11-01",
        size=10.5, color=RGBColor(0x9F, 0xAE, 0xCC))
notes(s, "这是一份把分析报告与图表合并的完整汇报版：前半部分讲数据、设计和参数，"
         "中间是 7 个亚型的结果，后面是生物学解读、局限和结论。")

# 2 ---------------------------------------------------------------- agenda
s = add_slide(prs)
header(s, "汇报提纲", None)
items = [
    ("01", "背景与科学问题", "为什么看小胶质细胞亚型间通讯"),
    ("02", "数据与设计", "7 亚型、AD vs 对照、receiver/sender 设计"),
    ("03", "方法与参数", "DE 阈值、先验网络、配体活性与信号通路"),
    ("04", "结果", "DE、配体活性、配体-靶基因、配体-受体、三色热图"),
    ("05", "生物学解读", "炎症增强 + 稳态减弱；亚型特异"),
    ("06", "局限与结论", "数据限制、可检验假设、下一步"),
]
y = 1.5
for num, head, sub in items:
    textbox(s, 0.75, y, 0.8, 0.5, num, size=20, bold=True, color=LIGHTBLUE)
    textbox(s, 1.6, y - 0.02, 6.0, 0.45, head, size=17, bold=True, color=NAVY)
    textbox(s, 1.6, y + 0.40, 9.5, 0.4, sub, size=11, color=GREY)
    y += 0.88
footer(s, 2, TOTAL)
notes(s, "先交代为什么做、用什么数据和方法，再逐层展示结果与解释。")

# 3 ---------------------------------------------------------------- background
s = add_slide(prs)
header(s, "背景与科学问题", "AD 中的小胶质细胞不是单一群体，而是多个功能状态的集合")
bullets(s, [
    "单细胞图谱把 AD 脑内小胶质细胞分为稳态（Homeos1/2/3）、炎症型 DAM（Inflam.DAM）、"
    "脂质型 DAM（Lipo.DAM）、核糖体型 DAM（Ribo.DAM1/2）等状态",
    "AD 中 DAM 亚群扩增、稳态亚群减少，但“谁在调控谁”仍不清楚",
    "NicheNet 可以回答：哪些由其他细胞（或亚型）表达的配体，能解释接收细胞的转录变化",
], 0.65, 1.45, 7.2, 3.4, size=13)
callout(s, 0.65, 4.75, 12.0, 1.35,
        "本次要回答的两个问题：\n"
        "① AD 中哪些配体驱动了小胶质细胞（尤其稳态亚群）的转录改变？\n"
        "② 这些配体来自哪个亚型、通过什么受体与下游通路起作用？", size=12)
footer(s, 3, TOTAL)
notes(s, "背景：小胶质细胞异质性 → DAM 扩增；NicheNet 用于从配体角度解释接收细胞的转录变化。")

# 4 ---------------------------------------------------------------- data
s = add_slide(prs)
header(s, "数据与设计", "仅保留 7 个小胶质细胞亚群；每个亚型内部做 AD vs 对照差异分析")
bullets(s, [
    "对象：scRNA（61,388 genes × 48,347 cells，9 个亚群）",
    "剔除 DIMs 与 MAC 巨噬细胞：38,664 cells / 7 亚群",
    "分组：AD 20,036 vs No Neuropathology 28,311（全图谱）",
    "receiver：轮流为 7 个亚型之一；sender：7 个亚群全部（含自分泌）",
    "每个 receiver 独立完成 DE → 配体活性 → 下游，共 7 轮",
], 0.6, 1.45, 6.5, 4.2, size=12.5)
rows = [
    ["亚型", "细胞数", "AD", "对照"],
    ["Homeos1", "12,775", "5,162", "7,613"],
    ["Homeos2", "4,582", "1,748", "2,834"],
    ["Homeos3", "711", "296", "415"],
    ["Inflam.DAM", "13,214", "6,066", "7,148"],
    ["Lipo.DAM", "1,512", "881", "631"],
    ["Ribo.DAM1", "4,307", "1,461", "2,846"],
    ["Ribo.DAM2", "1,563", "668", "895"],
]
table(s, rows, 7.35, 1.45, 5.4, 3.9, [1.55, 1.2, 1.2, 1.45], font_size=10.5)
textbox(s, 7.35, 5.55, 5.4, 0.8,
        "注：Homeos3 仅 711 cells（AD 296 / 对照 415），\n统计功效明显受限。", size=10, color=GREY)
footer(s, 4, TOTAL)
notes(s, "数据规模与亚型构成。AD/对照在每个亚型中都接近 2:1，没有出现极端失衡；"
         "但不同研究对两组的贡献不平衡，这一点在局限页说明。")

# 5 ---------------------------------------------------------------- design
s = add_slide(prs)
header(s, "分析设计：每个亚型轮流当 receiver", "共 7 轮；sender 始终是 7 个亚群（含自身，允许自分泌）")
for i, (name, color) in enumerate([("Homeos1", NAVY), ("Homeos2", BLUE), ("Homeos3", LIGHTBLUE),
                                   ("Inflam.DAM", RED), ("Lipo.DAM", SALMON),
                                   ("Ribo.DAM1", GREEN), ("Ribo.DAM2", LIGHTGREEN)]):
    x = 0.7 + i * 1.78
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.65),
                             Inches(1.6), Inches(0.75))
    box.fill.solid(); box.fill.fore_color.rgb = color; box.line.fill.background()
    textbox(s, x, 1.83, 1.6, 0.4, name, size=10.5, bold=True,
            color=WHITE if name not in ("Homeos3", "Ribo.DAM2") else NAVY,
            align=PP_ALIGN.CENTER)
textbox(s, 0.7, 2.55, 12.0, 0.35, "7 个亚群（既是 sender，也轮流做 receiver）", size=10,
        color=GREY, align=PP_ALIGN.CENTER)
rows = [
    ["轮次", "receiver（接收）", "sender（发送）", "比较"],
    ["1", "Homeos1", "7 个亚群全部", "AD vs 对照"],
    ["2", "Homeos2", "7 个亚群全部", "AD vs 对照"],
    ["3", "Homeos3", "7 个亚群全部", "AD vs 对照"],
    ["4", "Inflam.DAM", "7 个亚群全部", "AD vs 对照"],
    ["5", "Lipo.DAM", "7 个亚群全部", "AD vs 对照"],
    ["6", "Ribo.DAM1", "7 个亚群全部", "AD vs 对照"],
    ["7", "Ribo.DAM2", "7 个亚群全部", "AD vs 对照"],
]
table(s, rows, 0.7, 3.05, 11.9, 3.1, [1.4, 4.2, 4.0, 2.3], font_size=10.5)
textbox(s, 0.7, 6.30, 12.0, 0.5,
        "注意：这里做的是“亚型内部 AD vs 对照”的差异分析，不是亚型之间的 marker 分析。",
        size=10.5, bold=True, color=RED)
footer(s, 5, TOTAL)
notes(s, "这是设计上最关键的一点：receiver 内部比较 AD 与对照，避免把亚型构成变化误当成差异表达。")

# 6 ---------------------------------------------------------------- workflow
s = add_slide(prs)
header(s, "分析流程", "五步；每一步的输出都保存为表格或图，可追溯")
steps = [
    ("① 亚型内 DE", "FindMarkers\nAD vs 对照"),
    ("② 配体活性", "predict_ligand_activities\nPearson / AUPR"),
    ("③ 配体→靶基因", "调控潜力\nget_weighted_ligand_target_links"),
    ("④ 配体→受体", "LR 网络过滤\n热图 / Circos / LFC"),
    ("⑤ 信号通路", "ligand→受体→TF→靶基因\nTF 支持度"),
]
x = 0.62
for i, (t, d) in enumerate(steps):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.85),
                             Inches(2.2), Inches(2.3))
    box.fill.solid(); box.fill.fore_color.rgb = PALE
    box.line.color.rgb = LIGHTBLUE; box.line.width = Pt(1)
    textbox(s, x + 0.1, 2.0, 2.0, 0.4, t, size=13.5, bold=True, color=NAVY,
            align=PP_ALIGN.CENTER)
    textbox(s, x + 0.1, 2.5, 2.0, 1.5, d, size=10, color=DARKGREY, align=PP_ALIGN.CENTER)
    if i < len(steps) - 1:
        arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.26),
                                   Inches(2.8), Inches(0.28), Inches(0.42))
        arrow.fill.solid(); arrow.fill.fore_color.rgb = LIGHTBLUE
        arrow.line.fill.background()
    x += 2.54
textbox(s, 0.62, 4.45, 12.1, 1.6,
        "每个 receiver 输出 12 类图 + 9 张表；跨亚型再做汇总：配体 × 亚型活性热图、"
        "ALL_receivers_ligand_activity_*.csv、SUMMARY_overview.csv。\n"
        "下游还包含：配体在 sender 中的 LFC（三色热图）、配体-受体 LFC 图、"
        "以及 ligand→受体→TF→靶基因 的 TF 支持度热图。", size=11, color=GREY)
footer(s, 6, TOTAL)
notes(s, "流程五步走，最后一步是本轮新增的信号通路分析。")

# 7 ---------------------------------------------------------------- params
s = add_slide(prs)
header(s, "方法与参数", "所有阈值都写进脚本 cfg，可一键改动复现")
left = [
    "差异分析",
    ("FindMarkers（Wilcoxon），ident.1 = AD，ident.2 = No Neuropathology", 1),
    ("min.pct = 0.1，logfc.threshold = 0；padj < 0.05、|log2FC| ≥ 0.25", 1),
    ("两组检出率 ≥ 10%，剔除 MT- 基因，按 |logFC| 取 top 200", 1),
    "配体活性",
    ("predict_ligand_activities，背景 = receiver 表达基因 ∩ 先验矩阵", 1),
    ("候选配体 170 个（sender 表达 ∩ lr_network）；按 Pearson 排序取 top 20", 1),
]
bullets(s, left, 0.6, 1.45, 6.3, 4.6, size=12)
right = [
    "先验网络",
    ("lr_network_human_21122021：4,986 对配体-受体", 1),
    ("ligand_target_matrix：33,354 genes × 1,226 ligands", 1),
    ("weighted_networks：lr_sig / gr（5,206 个 TF）", 1),
    "下游分析",
    ("配体-受体：仅保留 receiver 表达的受体", 1),
    ("信号通路：get_ligand_signaling_path_with_receptor，top_n_regulators = 3", 1),
    ("输出：275 个文件（图 + 表 + 可导入 Cytoscape 的边表）", 1),
]
bullets(s, right, 6.95, 1.45, 6.0, 4.6, size=12)
callout(s, 0.6, 6.15, 12.2, 0.65,
        "可复现：Rscript NicheNet_7subtypes_AD.R；DE 结果有缓存，全量重跑约 15–19 分钟。")
footer(s, 7, TOTAL)
notes(s, "参数与网络版本都固定下来，方便审稿时复现。")

# 8 ---------------------------------------------------------------- DE table
s = add_slide(prs)
header(s, "结果 1｜各亚型 AD vs 对照差异基因", "在各自亚型内部比较，避免亚型构成变化带来的假差异")
rows = [
    ["receiver", "显著 DE", "上调基因集", "下调基因集", "top 上调配体", "top 下调配体"],
    ["Homeos1", "2,909", "200", "200", "LY86", "TGFB1"],
    ["Homeos2", "1,091", "68", "200", "IL18", "IL1B"],
    ["Homeos3", "143", "17*", "89", "—", "TGFB1"],
    ["Inflam.DAM", "2,627", "200", "200", "NLGN1", "TGFB1"],
    ["Lipo.DAM", "1,127", "200", "200", "LY86", "TNFRSF14"],
    ["Ribo.DAM1", "1,349", "200", "200", "LY86", "TGFB1"],
    ["Ribo.DAM2", "492", "169", "200", "LY86", "CALM3"],
]
table(s, rows, 0.6, 1.45, 12.15, 3.4,
      [1.6, 1.2, 1.5, 1.5, 2.6, 2.6], font_size=11)
textbox(s, 0.6, 5.05, 12.1, 1.0,
        "* Homeos3 上调基因仅 17 个（< 20），配体活性自动跳过，因此上调汇总图没有该列；"
        "下调方向 89 个基因，正常参与分析。", size=10.5, color=GREY)
callout(s, 0.6, 6.05, 12.15, 0.7,
        "解读：DAM 亚群（Inflam/Lipo/Ribo）差异基因最多（1,127–2,627），AD 的主要转录扰动发生在激活态亚群内部。")
footer(s, 8, TOTAL)
notes(s, "DE 数量与亚型规模一致；DAM 亚群变化最剧烈。Homeos3 的上调基因不足 20 个，"
         "配体活性被跳过，这是为什么上调汇总热图只有 6 列。")

# 9 ---------------------------------------------------------------- DE narrative
s = add_slide(prs)
header(s, "结果 1 解读｜扰动集中在 DAM，稳态亚群更像“接收方”", None)
bullets(s, [
    "三个 DAM 亚群检出 1,127–2,627 个差异基因，而稳态亚群 Homeos2/3 仅 1,091 / 143 个",
    "说明 AD 的主要转录改变发生在激活态亚群内部，稳态亚群的变化更细微",
    "因此把稳态亚群作为 receiver、DAM 作为主要 sender，更符合“谁被调控”的生物学问题",
    "Homeos1 的 DE 数最多（2,909），但它是数量最大的稳态亚群，部分反映细胞数与统计功效",
], 0.65, 1.45, 12.1, 3.6, size=13)
callout(s, 0.65, 5.35, 12.1, 1.1,
        "分析策略上的含义：与其问“DAM 自己怎么变”，不如问“稳态小胶质细胞接收到了什么信号”。\n"
        "这正是后面 7 轮 receiver 设计的出发点。", size=11.5)
footer(s, 9, TOTAL)
notes(s, "把 DE 结果转成分析策略：DAM 是变化的主体，稳态亚群是被调控的对象。")

# 10 --------------------------------------------------------------- up heatmap
s = add_slide(prs)
header(s, "结果 2｜配体活性总览（上调方向）",
       "每个亚型取 top 15 配体的并集；颜色 = 配体活性（Pearson）")
image_fit(s, os.path.join(BASE, "SUMMARY_ligand_activity_heatmap_up.png"),
          0.55, 1.35, 6.0, 5.55)
bullets(s, [
    "LY86 在 4/7 个亚型（Homeos1、Lipo.DAM、Ribo.DAM1、Ribo.DAM2）排名第一",
    "NLGN1 在 Inflam.DAM 第一；IL18 在 Homeos2 第一",
    "HLA-F / HLA-DMA / CD14 / B2M：抗原提呈与髓系活化模块",
    "Homeos3 因上调基因仅 17 个（< 20）未纳入，故只有 6 列",
], 6.9, 1.55, 5.9, 4.6, size=11.5)
callout(s, 6.9, 5.75, 5.9, 0.85,
        "跨亚型共性：DAM 亚群 → 稳态小胶质的“炎症配体”输入。", size=10.5)
footer(s, 10, TOTAL)
notes(s, "汇总热图：行是配体，列是 receiver。LY86 是最普遍的共享配体；"
         "Homeos3 缺列的原因是基因数不足，不是分析遗漏。")

# 11 --------------------------------------------------------------- down heatmap
s = add_slide(prs)
header(s, "结果 2｜配体活性总览（下调方向）",
       "下调基因对应的配体：提示哪些信号在 AD 中减弱")
image_fit(s, os.path.join(BASE, "SUMMARY_ligand_activity_heatmap_down.png"),
          0.55, 1.3, 4.7, 5.6)
bullets(s, [
    "TGFB1 在 4/7 个亚型（Homeos1、Homeos3、Inflam.DAM、Ribo.DAM1）排名第一",
    "IL1B（Homeos2）、TNFRSF14（Lipo.DAM）、CALM3（Ribo.DAM2）为亚型特异",
    "APOE、GAS6、ENG、RECK 反复出现，指向脂质/吞噬与血管通路",
    "下调方向活性整体低于上调（0.03–0.10），符合“信号减弱”而非“新信号出现”",
], 5.55, 1.55, 7.2, 4.6, size=12)
callout(s, 5.55, 5.95, 7.2, 0.8,
        "核心推断：AD 中小胶质细胞丢失 TGF-β 稳态信号。", color=RED, size=11)
footer(s, 11, TOTAL)
notes(s, "下调方向 7 列齐全（Homeos3 有 89 个下调基因）。TGFB1 反复居首。")

# 12 --------------------------------------------------------------- LY86
s = add_slide(prs)
header(s, "关键发现 ①｜LY86（MD-2）是上调方向的首要共享配体",
       "Homeos1 / Lipo.DAM / Ribo.DAM1 / Ribo.DAM2 均排名第一")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "01_ligand_activity_bar_up.png"),
          0.55, 1.35, 5.3, 5.5)
bullets(s, [
    "LY86 编码 MD-2，是 TLR4 的共受体，介导 LPS/内源性配体的先天免疫识别",
    "AD 中上调，靶基因富集于炎症与抗原提呈（HLA-DMA、CD14、B2M）",
    "Homeos1 中活性 0.159，明显高于第二名 NLGN1（0.099）",
    "注意：LR 网络中没有 LY86–TLR4 注释，配体-受体图中 LY86 无对应受体",
], 6.15, 1.55, 6.6, 3.9, size=11.5)
callout(s, 6.15, 5.55, 6.6, 1.0,
        "证据链：LY86 表达↑ → MD-2 与 TLR4 组装 → NF-κB 激活 →\n"
        "HLA-DMA / CD14 / B2M 等炎症与抗原提呈基因↑", size=10)
footer(s, 12, TOTAL)
notes(s, "LY86/MD-2 是最稳健的共享配体；但受体层面受网络注释限制。")

# 13 --------------------------------------------------------------- TGFB1
s = add_slide(prs)
header(s, "关键发现 ②｜TGFB1 下调方向反复居首",
       "提示 AD 中小胶质细胞的 TGF-β 稳态信号减弱")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "01_ligand_activity_bar_down.png"),
          0.55, 1.35, 5.3, 5.5)
bullets(s, [
    "TGFB1 靶基因在 AD 中整体下调，说明下游转录程序被抑制",
    "受体：TGFBR1 / TGFBR2 / ENG，均在 receiver 表达",
    "TGF-β 是小胶质细胞维持稳态、抑制过度激活的关键因子",
    "与 DAM 扩增、稳态亚群减少的表型一致：稳态信号减弱 → 去抑制",
], 6.15, 1.55, 6.6, 3.9, size=11.5)
callout(s, 6.15, 5.55, 6.6, 1.0,
        "可检验假设：AD 中 TGF-β 通路活性下降 → 稳态程序丢失。\n"
        "可用 TGFBR1/2 下游（SMAD2/3 磷酸化）或通路评分在蛋白/组织层面验证。", size=10)
footer(s, 13, TOTAL)
notes(s, "TGF-β 是维持小胶质稳态的核心；其靶基因下调提示保护性信号丢失。")

# 14 --------------------------------------------------------------- subtype table
s = add_slide(prs)
header(s, "结果 3｜亚型特异信号", "同一套先验网络下，不同 receiver 的优先配体不同")
rows = [
    ["receiver", "top 上调配体", "top 下调配体", "主要受体", "可能的生物学过程"],
    ["Homeos1", "LY86 / NLGN1", "TGFB1 / APOE", "TGFBR1/2, TREM2, SORL1", "稳态维持、脂质代谢"],
    ["Homeos2", "IL18 / JAM2", "IL1B / TGFB1", "IL1RAP, IL1RAPL1", "炎症小体、IL-1 家族"],
    ["Homeos3", "—（基因不足）", "TGFB1 / TIMP1", "TGFBR1/2, CD63", "基质重塑（样本量小）"],
    ["Inflam.DAM", "NLGN1 / LY86", "TGFB1 / ENG", "TGFBR1/2, ENG", "炎症活化、血管生成"],
    ["Lipo.DAM", "LY86 / NLGN1", "TNFRSF14 / APOE", "TREM2, SORL1, LRP1", "脂质处理、吞噬"],
    ["Ribo.DAM1", "LY86 / NLGN1", "TGFB1 / GAS6", "TGFBR1/2, AXL, MERTK", "核糖体应激、吞噬"],
    ["Ribo.DAM2", "LY86 / TF", "CALM3 / GAS6", "AXL, MERTK", "钙信号、吞噬"],
]
table(s, rows, 0.55, 1.42, 12.25, 4.4,
      [1.55, 2.35, 2.35, 2.6, 3.4], font_size=9.5)
textbox(s, 0.55, 6.05, 12.2, 0.85,
        "共性：DAM 亚群普遍以 TGF-β 与吞噬相关配体（GAS6–AXL/MERTK、APOE–TREM2）与稳态亚群通讯；"
        "差异集中在 IL-1/IL-18 与 TNFRSF14 上。", size=10, color=GREY)
footer(s, 14, TOTAL)
notes(s, "亚型特异性：同一网络、不同 receiver，优先配体随之改变，说明结果不是网络偏倚的单一投影。")

# 15 --------------------------------------------------------------- ligand-target
s = add_slide(prs)
header(s, "结果 4｜配体 → 靶基因调控潜力", "以 Homeos1 上调方向为例")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "03_ligand_target_heatmap_up.png"),
          0.5, 1.3, 7.6, 5.55)
bullets(s, [
    "行 = 优先配体，列 = 预测靶基因，颜色 = regulatory potential",
    "LY86 靶基因包括 HLA-DMA、CD14、B2M 等",
    "IL18/IL1B 共享 NFKBIA、SAT1 等靶基因，提示 NF-κB",
    "该矩阵是配体-受体与信号通路分析的输入",
], 8.3, 1.55, 4.5, 4.8, size=11)
footer(s, 15, TOTAL)
notes(s, "配体-靶基因是 NicheNet 的核心输出，用于后续所有下游图。")

# 16 --------------------------------------------------------------- LR
s = add_slide(prs)
header(s, "结果 5｜配体–受体：谁在接收信号", "Circos 展示配体-受体对；LFC 图展示配体/受体在 AD 中的变化")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "07_ligand_receptor_circos_up.png"),
          0.45, 1.42, 5.0, 4.7)
image_fit(s, os.path.join(BASE, "receiver_Lipo.DAM", "11_ligand_receptor_lfc_up.png"),
          5.6, 1.7, 7.3, 3.3)
textbox(s, 0.45, 6.30, 12.4, 0.65,
        "Circos 中配体按表达最高的 sender 亚型着色（蓝系 = 稳态亚群，红绿 = DAM）；"
        "右图显示 Lipo.DAM 中 HLA-DMA–CD74、CD14–PLXND1 等配体/受体在 AD 中上调。",
        size=9.5, color=GREY)
footer(s, 16, TOTAL)
notes(s, "配体-受体的两种视角：网络（Circos）与条件变化（LFC 图）。")

# 17 --------------------------------------------------------------- LFC heatmap
s = add_slide(prs)
header(s, "结果 6｜三色热图 ①：配体在各 sender 亚型中的 LFC",
       "蓝 = AD 中下调，红 = AD 中上调（make_threecolor_heatmap_ggplot）")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "09_ligand_lfc_sender_heatmap_up.png"),
          0.55, 1.35, 7.0, 5.5)
bullets(s, [
    "HLA-DMA 在 Inflam.DAM 中强烈上调（MHC-II 抗原提呈）",
    "CD14 在多个亚型中上调（TLR4 共受体）",
    "NLGN4Y / NLGN1 在多数亚型中下调——更可能是环境 RNA",
    "用于判断配体变化发生在哪个亚型，而不只是“哪个配体活跃”",
], 7.85, 1.55, 4.95, 4.8, size=11)
footer(s, 17, TOTAL)
notes(s, "把配体变化定位到具体 sender 亚型，避免把全局表达差异误读为亚型特异。")

# 18 --------------------------------------------------------------- signaling
s = add_slide(prs)
header(s, "结果 7｜三色热图 ②：配体–靶基因链接的 TF 支持度",
       "颜色 = 连接该配体与靶基因的转录因子数量（白 → 深紫）")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "12_signaling_threecolor_heatmap_up.png"),
          0.55, 1.35, 8.3, 4.7)
bullets(s, [
    "沿 ligand→受体→信号→TF→靶基因 推断路径",
    "颜色越深表示越多 TF 支持该链接",
    "DAM 相关配体的链接普遍获得 20–30 个 TF 支持",
    "先验网络本身高度连通，该图适合作一致性检查",
], 9.05, 1.55, 3.8, 4.6, size=10.5)
footer(s, 18, TOTAL)
notes(s, "TF 支持度来自同一套先验网络，存在循环性，解释时需谨慎。")

# 19 --------------------------------------------------------------- model
s = add_slide(prs)
header(s, "生物学解读｜炎症增强 + 稳态减弱的双向模型", None)
send = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.55),
                          Inches(3.2), Inches(4.1))
send.fill.solid(); send.fill.fore_color.rgb = RGBColor(0xF8, 0xE3, 0xDF)
send.line.color.rgb = RED; send.line.width = Pt(1.5)
textbox(s, 0.85, 1.70, 2.9, 0.4, "Sender：DAM 亚群", size=13.5, bold=True, color=RED)
textbox(s, 0.85, 2.15, 2.9, 3.3,
        "Inflam.DAM\nLipo.DAM\nRibo.DAM1/2\n\n分泌：LY86、IL1B、\nIL18、APOE、GAS6、\nTNFRSF14",
        size=10.5, color=DARKGREY)
recv = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.4), Inches(1.55),
                          Inches(3.2), Inches(4.1))
recv.fill.solid(); recv.fill.fore_color.rgb = RGBColor(0xE1, 0xEC, 0xF6)
recv.line.color.rgb = BLUE; recv.line.width = Pt(1.5)
textbox(s, 9.55, 1.70, 2.9, 0.4, "Receiver：稳态小胶质", size=13.5, bold=True, color=BLUE)
textbox(s, 9.55, 2.15, 2.9, 3.3,
        "Homeos1/2/3\n\n受体：TGFBR1/2、\nTREM2、SORL1、\nAXL、MERTK、IL1RAP",
        size=10.5, color=DARKGREY)
arrows = [
    ("LY86 → TLR4（未注释）｜炎症/抗原提呈 ↑", 2.35, NAVY),
    ("TGFB1 → TGFBR1/2｜稳态程序 ↓", 3.30, BLUE),
    ("APOE → TREM2/SORL1｜脂质代谢 ↓", 4.25, GREEN),
    ("GAS6 → AXL/MERTK｜吞噬功能 ↓", 5.20, GREY),
]
for text, y, color in arrows:
    arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.15), Inches(y),
                             Inches(4.9), Inches(0.42))
    arr.fill.solid(); arr.fill.fore_color.rgb = color
    arr.line.fill.background()
    textbox(s, 4.15, y - 0.34, 4.95, 0.32, text, size=9, color=color,
            align=PP_ALIGN.CENTER)
textbox(s, 0.6, 5.95, 12.2, 0.9,
        "模型：AD 中 DAM 亚群扩增并释放炎症配体（LY86、IL1B/IL18），同时 TGF-β、APOE–TREM2、"
        "GAS6–AXL 等稳态/吞噬信号减弱，导致稳态小胶质细胞去抑制、向激活态转化。",
        size=11, color=DARKGREY)
footer(s, 19, TOTAL)
notes(s, "综合模型：一边是炎症输入增强，一边是稳态/吞噬支持减弱。")

# 20 --------------------------------------------------------------- literature
s = add_slide(prs)
header(s, "与已知 AD 机制的对照", "以下为文献背景，用于解释方向一致性，不是本次数据直接证明")
rows = [
    ["本次结果", "已知机制/文献背景", "一致性"],
    ["APOE → TREM2 / SORL1 / LRP1（下调方向）", "APOE–TREM2 是 AD 最强的遗传风险轴，调控小胶质脂质代谢与吞噬", "方向一致"],
    ["TGFB1 靶基因下调", "TGF-β 维持小胶质稳态、抑制过度激活；通路减弱与激活态扩增相符", "方向一致"],
    ["LY86（MD-2）上调", "TLR4/MD-2 识别 Aβ 与 DAMPs，驱动神经炎症", "方向一致"],
    ["GAS6 → AXL / MERTK 下调", "GAS6–AXL/MERTK 参与凋亡细胞清除；吞噬受损是 AD 表型之一", "方向一致"],
    ["IL1B / IL18（Homeos2）", "NLRP3 炎症小体–IL-1β/IL-18 轴在 AD 中激活", "亚型特异"],
]
table(s, rows, 0.55, 1.42, 12.25, 4.1, [4.2, 6.4, 1.8], font_size=9.5)
textbox(s, 0.55, 5.75, 12.2, 0.8,
        "说明：这些对应关系支持结果的可信度，但不能替代功能实验；下一步建议做通路评分与配体中和实验。",
        size=10, color=GREY)
footer(s, 20, TOTAL)
notes(s, "把结果放回 AD 已知机制里对照，强调是“方向一致”而不是因果证明。")

# 21 --------------------------------------------------------------- limitations
s = add_slide(prs)
header(s, "局限性与注意事项", None)
bullets(s, [
    ("批次/研究混杂：AD 与对照在不同研究的贡献不平衡（Leng 2021 全为 AD、Franjic 2022 全为对照），"
     "DE 未校正研究来源；建议 pseudobulk + 研究作为协变量做敏感性分析", 0),
    ("环境 RNA：NLGN1/NLGN4Y/NRXN1 检出率仅 10–20%，很可能是 snRNA-seq 环境污染，不宜作为主结论", 0),
    ("LR 网络覆盖：LY86 的受体 TLR4 未收录在 21122021 版 lr_network；CALM3、UXS1 等胞内蛋白"
     "也被数据库列为配体", 0),
    ("先验网络循环性：配体-靶基因与信号通路推断共用同一套网络，TF 支持度高属预期", 0),
    ("统计功效：Homeos3 仅 711 cells，上调基因 17 个（< 20 被跳过），相关结论仅供参考", 0),
    ("未做细胞比例校正：AD 中亚型构成改变可能放大或掩盖亚型内差异", 0),
], 0.65, 1.45, 12.1, 5.0, size=12)
footer(s, 21, TOTAL)
notes(s, "主动说明六类局限，答辩时更有说服力。")

# 22 --------------------------------------------------------------- conclusion
s = add_slide(prs)
header(s, "结论", None)
items = [
    ("①", "建立 7 亚型 × AD/对照的 NicheNet 流程", "每亚型独立 DE、配体活性、配体-靶基因、配体-受体与信号通路，输出 275 个文件"),
    ("②", "LY86（MD-2）是最稳健的共享上调配体", "4/7 亚型排名第一，指向 TLR4 相关先天免疫激活"),
    ("③", "TGFB1 是下调方向的核心配体", "4/7 亚型排名第一，提示稳态 TGF-β 信号减弱"),
    ("④", "亚型特异信号清晰", "Homeos2：IL18/IL1B；Lipo.DAM：TNFRSF14/APOE–TREM2；Ribo：GAS6–AXL/MERTK"),
    ("⑤", "结果可直接用于文章", "配体活性表、配体-靶基因表、LR 对、Circos、三色热图与 signaling 边表"),
]
y = 1.45
for num, head, sub in items:
    textbox(s, 0.7, y, 0.6, 0.45, num, size=18, bold=True, color=LIGHTBLUE)
    textbox(s, 1.35, y - 0.03, 11.4, 0.4, head, size=15, bold=True, color=NAVY)
    textbox(s, 1.35, y + 0.36, 11.4, 0.45, sub, size=11, color=GREY)
    y += 1.02
footer(s, 22, TOTAL)
notes(s, "五条结论，与前面的图一一对应。")

# 23 --------------------------------------------------------------- appendix
s = add_slide(prs)
header(s, "附录｜结果文件与复现方式", None)
bullets(s, [
    "脚本：NicheNet_7subtypes_AD.R（含 cfg 参数、DE 缓存、12 类图与信号通路模块）",
    "结果：NicheNet_results_7subtypes/20261031_1842/",
    ("每个 receiver_XXX/ 含：DE 表、基因集、配体活性表、配体-靶基因表、LR 对表、signaling 边表", 1),
    ("以及 12 类图：01 配体活性条形图、02 直方图、03 配体-靶基因、04 配体-受体、05 DotPlot、"
     "06 靶基因热图、07 Circos、08 小提琴、09 LFC 三色、10 组合图、11 LR LFC、12 TF 支持度", 1),
    "跨亚型汇总：SUMMARY_ligand_activity_heatmap_up/down.png、ALL_receivers_ligand_activity_*.csv、"
    "SUMMARY_overview.csv",
    "复现：Rscript NicheNet_7subtypes_AD.R；DE 有缓存时全量约 15–19 分钟",
], 0.65, 1.45, 12.1, 4.6, size=11.5)
callout(s, 0.65, 6.05, 12.1, 0.65,
        "配套文档：NicheNet_7subtypes_AD_analysis.docx（文字版分析报告，可与本 PPT 对照阅读）")
footer(s, 23, TOTAL)
notes(s, "附录给出文件清单与复现命令。")

# 24 --------------------------------------------------------------- end
s = add_slide(prs)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(SH))
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
textbox(s, 1.0, 2.9, 11.3, 0.8, "谢谢！欢迎讨论", size=34, bold=True, color=WHITE)
textbox(s, 1.0, 3.9, 11.3, 0.5,
        "下一步：TGF-β / APOE–TREM2 通路评分验证、配体中和实验、pseudobulk 敏感性分析",
        size=13, color=RGBColor(0xD0, 0xD8, 0xEA))
textbox(s, 1.0, 6.2, 11.3, 0.4, "NicheNet · 7 个小胶质细胞亚型 · 2026-11-01", size=10,
        color=RGBColor(0x9F, 0xAE, 0xCC))
notes(s, "结束页：给出三条下一步计划。")

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
