# -*- coding: utf-8 -*-
"""Build the NicheNet 7-subtype summary deck (Chinese, 16:9)."""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from PIL import Image

BASE = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                    "NicheNet_results_7subtypes", "20261031_1842")
OUT = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                   "NicheNet_7subtypes_AD_summary.pptx")

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


def set_run_font(run, size=None, bold=None, color=None, name=FONT):
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
    if color is not None:
        run.font.color.rgb = color


def textbox(slide, left, top, width, height, text, size=14, bold=False,
            color=DARKGREY, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
            line_spacing=1.15, font=FONT):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.02)
    tf.margin_right = Inches(0.02)
    tf.margin_top = Inches(0.01)
    tf.margin_bottom = Inches(0.01)
    lines = text.split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        run = p.add_run()
        run.text = line
        set_run_font(run, size=size, bold=bold, color=color, name=font)
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


def footer(slide, page):
    textbox(slide, 0.55, 7.08, 8.0, 0.28,
            "NicheNet · 7 个小胶质细胞亚型 · AD vs No Neuropathology", size=9, color=GREY)
    textbox(slide, 11.9, 7.08, 0.9, 0.28, f"{page}", size=9, color=GREY,
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
    return l, t, w, h


def bullets(slide, items, left, top, width, height, size=13, color=DARKGREY,
            bullet_color=NAVY):
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.02); tf.margin_right = Inches(0.02)
    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.level = level
        p.space_after = Pt(6)
        p.line_spacing = 1.2
        marker = "▪ " if level == 0 else "– "
        r0 = p.add_run(); r0.text = marker
        set_run_font(r0, size=size, bold=False, color=bullet_color)
        r1 = p.add_run(); r1.text = text
        set_run_font(r1, size=size - (1 if level else 0), bold=False, color=color)
    return box


def table(slide, rows, left, top, width, height, col_widths, font_size=11,
          header_fill=NAVY, header_color=WHITE, zebra=PALE):
    n_rows, n_cols = len(rows), len(rows[0])
    shape = slide.shapes.add_table(n_rows, n_cols, Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    tbl = shape.table
    for i, w in enumerate(col_widths):
        tbl.columns[i].width = Inches(w)
    for r in range(n_rows):
        for c in range(n_cols):
            cell = tbl.cell(r, c)
            cell.text = ""
            cell.margin_left = Inches(0.06)
            cell.margin_right = Inches(0.04)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if c > 0 else PP_ALIGN.LEFT
            run = p.add_run(); run.text = str(rows[r][c])
            if r == 0:
                set_run_font(run, size=font_size, bold=True, color=header_color)
                cell.fill.solid(); cell.fill.fore_color.rgb = header_fill
            else:
                set_run_font(run, size=font_size,
                             bold=(c == 0), color=DARKGREY)
                cell.fill.solid()
                cell.fill.fore_color.rgb = zebra if r % 2 == 0 else WHITE
    return tbl


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def callout(slide, left, top, width, height, text, color=NAVY, size=11):
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top),
                                 Inches(width), Inches(height))
    box.fill.solid(); box.fill.fore_color.rgb = PALE
    box.line.color.rgb = LIGHTBLUE; box.line.width = Pt(1)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.12); tf.margin_right = Inches(0.12)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    run = p.add_run(); run.text = text
    set_run_font(run, size=size, bold=True, color=color)


prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)

# ---------------------------------------------------------------- 1 cover
s = add_slide(prs)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(SW), Inches(SH))
bg.fill.solid(); bg.fill.fore_color.rgb = NAVY; bg.line.fill.background()
textbox(s, 1.0, 2.2, 11.3, 0.4, "AD 脑内小胶质细胞亚型间通讯", size=18,
        color=LIGHTBLUE)
textbox(s, 1.0, 2.65, 11.3, 1.0,
        "NicheNet 配体–靶基因–受体–信号通路分析", size=36, bold=True, color=WHITE)
textbox(s, 1.0, 3.75, 11.3, 0.5,
        "7 个亚型 × (AD vs No Neuropathology)，每个亚型各做一次 receiver",
        size=15, color=RGBColor(0xD0, 0xD8, 0xEA))
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(4.5),
                          Inches(3.0), Pt(2.5))
line.fill.solid(); line.fill.fore_color.rgb = SALMON; line.line.fill.background()
textbox(s, 1.0, 4.85, 11.3, 1.2,
        "数据：scRNA.RData（48,347 cells，去除 DIMs / MAC 后 38,664 cells）\n"
        "结果：NicheNet_results_7subtypes/20261031_1842",
        size=12, color=RGBColor(0xC8, 0xD2, 0xE6))
textbox(s, 1.0, 6.55, 11.3, 0.35, "2026-11-01", size=11,
        color=RGBColor(0x9F, 0xAE, 0xCC))
notes(s, "封面。说明数据来源、分析对象（7 个小胶质细胞亚型）与对比分组（AD vs No Neuropathology）。")

# ---------------------------------------------------------------- 2 data
s = add_slide(prs)
header(s, "数据与设计", "仅保留 7 个小胶质细胞亚群；每个亚型内部做 AD vs 对照差异分析")
bullets(s, [
    "对象：scRNA（61,388 genes × 48,347 cells，含 9 个亚群）",
    "剔除 DIMs 与 MAC 巨噬细胞后：38,664 cells / 7 亚群",
    "分组：AD 20,036 vs No Neuropathology 28,311（全图谱计数）",
    "receiver：轮流为 7 个亚型之一；sender：7 个亚群全部（含自分泌）",
    "每个 receiver 独立做 DE → 配体活性 → 下游图表，共 7 轮",
], 0.6, 1.45, 6.4, 4.6, size=13)

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
table(s, rows, 7.35, 1.5, 5.4, 3.9, [1.55, 1.2, 1.2, 1.45], font_size=11)

textbox(s, 7.35, 5.55, 5.4, 0.9,
        "注：AD/对照在 7 个亚型中均<10:1 失衡；\nHomeos3 仅 711 cells，统计功效有限。",
        size=10, color=GREY)
footer(s, 2)
notes(s, "数据概况：48,347 cells 的多研究整合图谱；去掉 DIMs、MAC 后 38,664 cells。"
         "注意不同研究对 AD/对照的贡献不平衡，后续 DE 未校正研究批次。")

# ---------------------------------------------------------------- 3 workflow
s = add_slide(prs)
header(s, "分析流程", "每个亚型作为 receiver 各跑一次，共 7 轮")
steps = [
    ("① 亚型内 DE", "FindMarkers\nAD vs 对照\npadj<0.05, |logFC|≥0.25"),
    ("② 配体活性", "predict_ligand_activities\nPearson / AUPR\n候选配体 170 个"),
    ("③ 配体→靶基因", "get_weighted_ligand_target_links\n调控潜力热图"),
    ("④ 配体→受体", "LR 网络过滤\n热图 / Circos / LFC"),
    ("⑤ 信号通路", "ligand→受体→TF→靶基因\nTF 支持度三色热图"),
]
x = 0.62
for i, (t, d) in enumerate(steps):
    box = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.05),
                             Inches(2.2), Inches(2.5))
    box.fill.solid(); box.fill.fore_color.rgb = PALE
    box.line.color.rgb = LIGHTBLUE; box.line.width = Pt(1)
    textbox(s, x + 0.1, 2.2, 2.0, 0.4, t, size=14, bold=True, color=NAVY,
            align=PP_ALIGN.CENTER)
    textbox(s, x + 0.1, 2.75, 2.0, 1.6, d, size=10, color=DARKGREY,
            align=PP_ALIGN.CENTER)
    if i < len(steps) - 1:
        arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x + 2.26),
                                   Inches(3.05), Inches(0.28), Inches(0.42))
        arrow.fill.solid(); arrow.fill.fore_color.rgb = LIGHTBLUE
        arrow.line.fill.background()
    x += 2.54

textbox(s, 0.62, 4.9, 12.1, 1.6,
        "每轮输出 12 类图 + 9 张表；跨亚型再做汇总：配体 × 亚型活性热图、"
        "ALL_receivers_ligand_activity_*.csv、SUMMARY_overview.csv。\n"
        "关键参数：top 200 上调/下调基因、表达检出率 10%、剔除 MT- 基因、"
        "配体活性按 Pearson 排序取 top 20。", size=11, color=GREY)
footer(s, 3)
notes(s, "流程说明：DE 用亚型内部 AD vs 对照，不是亚型间 marker；"
         "配体活性以接收细胞表达基因为背景，候选配体为 sender 表达且存在于先验网络。")

# ---------------------------------------------------------------- 4 DE
s = add_slide(prs)
header(s, "各亚型 AD vs 对照差异基因", "在各自亚型内部比较，避免亚型构成变化带来的假差异")
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
table(s, rows, 0.6, 1.5, 12.15, 3.5,
      [1.6, 1.2, 1.5, 1.5, 2.6, 2.6], font_size=11)
textbox(s, 0.6, 5.25, 12.1, 1.0,
        "* Homeos3 上调基因仅 17 个（<20），配体活性自动跳过。\n"
        "DAM 亚群（Inflam/Lipo/Ribo）DE 数量大（1,127–2,627），说明 AD 中激活态变化最剧烈；"
        "稳态亚群变化相对小（Homeos2/3）。", size=11, color=GREY)
callout(s, 0.6, 6.25, 12.15, 0.6,
        "解读：AD 的主要转录扰动发生在 DAM 亚群内部；稳态亚群更像“被调控方”，适合作为 receiver。")
footer(s, 4)
notes(s, "DE 基因数量与亚型规模一致。Homeos3 只有 711 cells，上调基因不足，配体活性跳过。")

# ---------------------------------------------------------------- 5 summary up
s = add_slide(prs)
header(s, "配体活性总览（上调方向）", "每个亚型取 top 15 配体的并集；颜色 = 配体活性（Pearson）")
image_fit(s, os.path.join(BASE, "SUMMARY_ligand_activity_heatmap_up.png"),
          0.55, 1.35, 6.0, 5.6)
bullets(s, [
    "LY86 在 4/7 个亚型（Homeos1、Lipo.DAM、Ribo.DAM1、Ribo.DAM2）排名第一",
    "NLGN1 在 Inflam.DAM 第一；IL18 在 Homeos2 第一",
    "HLA-F / HLA-DMA / CD14 / B2M：抗原提呈与髓系活化模块",
    "少数亚型（Homeos2/3）信号弱，与 DE 基因数少一致",
], 6.9, 1.55, 5.9, 4.8, size=12)
textbox(s, 6.9, 6.35, 5.9, 0.6,
        "跨亚型共性：DAM 亚群 → 稳态小胶质的“炎症配体”输入。", size=11,
        bold=True, color=NAVY)
footer(s, 5)
notes(s, "汇总热图：行是配体，列是 receiver 亚型。LY86 是最普遍的共享配体。")

# ---------------------------------------------------------------- 6 summary down
s = add_slide(prs)
header(s, "配体活性总览（下调方向）", "下调基因对应的配体：提示哪些信号在 AD 中减弱")
image_fit(s, os.path.join(BASE, "SUMMARY_ligand_activity_heatmap_down.png"),
          0.55, 1.3, 4.7, 5.65)
bullets(s, [
    "TGFB1 在 4/7 个亚型（Homeos1、Homeos3、Inflam.DAM、Ribo.DAM1）排名第一",
    "IL1B（Homeos2）、TNFRSF14（Lipo.DAM）、CALM3（Ribo.DAM2）为亚型特异",
    "APOE、GAS6、ENG、RECK 反复出现，指向脂质/吞噬与血管通路",
    "下调方向活性整体低于上调（0.03–0.10），符合“信号减弱”而非“新信号出现”",
], 5.55, 1.55, 7.2, 4.8, size=12)
textbox(s, 5.55, 6.35, 7.2, 0.6,
        "核心推断：AD 中小胶质细胞丢失 TGF-β 稳态信号。", size=11,
        bold=True, color=RED)
footer(s, 6)
notes(s, "下调方向的配体活性整体较弱但方向一致：TGFB1 反复居首。")

# ---------------------------------------------------------------- 7 LY86
s = add_slide(prs)
header(s, "关键发现 ①：LY86（MD-2）是上调方向的首要共享配体",
       "Homeos1 / Lipo.DAM / Ribo.DAM1 / Ribo.DAM2 均排名第一")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "01_ligand_activity_bar_up.png"),
          0.55, 1.35, 5.3, 5.55)
bullets(s, [
    "LY86 编码 MD-2，是 TLR4 的共受体，介导 LPS/内源性配体的先天免疫识别",
    "在 AD 中上调，且其靶基因富集于炎症与抗原提呈（HLA-DMA、CD14、B2M）",
    "Homeos1 中活性 0.159，明显高于第二名 NLGN1（0.099）",
    "注意：LR 网络中没有 LY86–TLR4 注释，因此配体-受体图中 LY86 无对应受体（见后页说明）",
], 6.15, 1.55, 6.6, 4.3, size=12)
callout(s, 6.15, 5.75, 6.6, 0.95,
        "证据链：LY86 表达↑ → MD-2 与 TLR4 组装 → NF-κB 激活 →\n"
        "HLA-DMA / CD14 / B2M 等炎症与抗原提呈基因↑", color=NAVY, size=10.5)
footer(s, 7)
notes(s, "LY86/MD-2 是 TLR4 共受体，是本次最稳健的共享配体；但 LR 网络覆盖不足，"
         "配体-受体环节需要单独说明。")

# ---------------------------------------------------------------- 8 TGFB1
s = add_slide(prs)
header(s, "关键发现 ②：TGFB1 下调方向反复居首",
       "提示 AD 中小胶质细胞的 TGF-β 稳态信号减弱")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "01_ligand_activity_bar_down.png"),
          0.55, 1.35, 5.3, 5.55)
bullets(s, [
    "TGFB1 靶基因在 AD 中整体下调，说明其下游转录程序被抑制",
    "受体：TGFBR1 / TGFBR2 / ENG（内皮糖蛋白），均在 receiver 表达",
    "TGF-β 是小胶质细胞维持稳态、抑制过度激活的关键因子",
    "与 DAM 亚群扩增、稳态亚群减少的表型一致：稳态信号减弱 → 去抑制",
], 6.15, 1.55, 6.6, 5.2, size=12)
footer(s, 8)
notes(s, "TGF-β 通路是维持小胶质细胞稳态的核心；其靶基因下调提示保护性信号丢失。")

# ---------------------------------------------------------------- 9 subtype specific
s = add_slide(prs)
header(s, "亚型特异信号", "同一套先验网络下，不同 receiver 的优先配体不同")
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
table(s, rows, 0.55, 1.45, 12.25, 4.6,
      [1.55, 2.35, 2.35, 2.6, 3.4], font_size=9.5)
textbox(s, 0.55, 6.25, 12.2, 0.7,
        "共性：DAM 亚群（Inflam/Lipo/Ribo）普遍以 TGF-β 与吞噬相关配体（GAS6–AXL/MERTK、APOE–TREM2）"
        "与稳态亚群通讯；差异集中在 IL-1/IL-18 与 TNFRSF14 上。", size=10, color=GREY)
footer(s, 9)
notes(s, "亚型特异性表格：每个 receiver 的 top 配体与受体组合，以及对应的生物学过程。")

# ---------------------------------------------------------------- 10 ligand-target
s = add_slide(prs)
header(s, "配体 → 靶基因调控潜力", "以 Homeos1 上调方向为例：LY86 的靶基因覆盖多个炎症模块")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "03_ligand_target_heatmap_up.png"),
          0.5, 1.3, 7.6, 5.65)
bullets(s, [
    "行 = 优先配体，列 = 预测靶基因，颜色 = regulatory potential",
    "LY86 靶基因包括 HLA-DMA、CD14、B2M、TGFB1 等",
    "IL18/IL1B 共享一批靶基因（NFKBIA、SAT1 等），提示下游 NF-κB",
    "该矩阵用于构建后续配体-受体与信号通路图",
], 8.3, 1.55, 4.5, 5.2, size=11)
footer(s, 10)
notes(s, "调控潜力热图展示配体对靶基因的预测强度，是 NicheNet 的核心输出。")

# ---------------------------------------------------------------- 11 LR
s = add_slide(prs)
header(s, "配体–受体：谁在接收信号", "Circos 展示配体-受体对；LFC 图展示配体/受体在 AD 中的变化")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "07_ligand_receptor_circos_up.png"),
          0.45, 1.45, 5.2, 4.9)
image_fit(s, os.path.join(BASE, "receiver_Lipo.DAM", "11_ligand_receptor_lfc_up.png"),
          5.75, 1.75, 7.2, 3.4)
textbox(s, 0.45, 6.45, 12.4, 0.6,
        "Circos 中配体按表达最高的 sender 亚型着色（蓝系 = 稳态亚群，红绿 = DAM）；"
        "右图显示 Lipo.DAM 中 HLA-DMA–CD74、CD14–PLXND1 等配体/受体在 AD 中上调。",
        size=10, color=GREY)
footer(s, 11)
notes(s, "Circos 的 sender 归属按配体表达最高亚型自动分配；右图是配体-受体层面的 LFC。")

# ---------------------------------------------------------------- 12 LFC heatmap
s = add_slide(prs)
header(s, "三色热图 ①：配体在各 sender 亚型中的 AD vs 对照 LFC",
       "蓝 = AD 中下调，红 = AD 中上调（make_threecolor_heatmap_ggplot）")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "09_ligand_lfc_sender_heatmap_up.png"),
          0.55, 1.35, 7.2, 5.6)
bullets(s, [
    "HLA-DMA 在 Inflam.DAM 中强烈上调（MHC-II 抗原提呈）",
    "CD14 在多个亚型中上调（TLR4 共受体）",
    "NLGN4Y / NLGN1 在多数亚型中下调 —— 更可能是环境 RNA 而非真实信号",
    "用于判断配体变化发生在哪个亚型，而不仅是“哪个配体活跃”",
], 8.0, 1.55, 4.8, 5.2, size=11)
footer(s, 12)
notes(s, "三色 LFC 热图把配体变化定位到具体 sender 亚型，避免把全局表达差异误读为亚型特异。")

# ---------------------------------------------------------------- 13 signaling
s = add_slide(prs)
header(s, "三色热图 ②：配体–靶基因链接的 TF 支持度",
       "颜色 = 连接该配体与靶基因的转录因子数量（白 → 深紫）")
image_fit(s, os.path.join(BASE, "receiver_Homeos1", "12_signaling_threecolor_heatmap_up.png"),
          0.55, 1.35, 8.4, 4.8)
bullets(s, [
    "沿 ligand→受体→信号→TF→靶基因 推断路径",
    "颜色越深表示越多 TF 支持该链接",
    "DAM 亚群相关配体的链接普遍获得 20–30 个 TF 支持",
    "提示：先验网络本身高度连通，该图更适合作为一致性检查，而非独立证据",
], 9.15, 1.55, 3.7, 5.0, size=10.5)
footer(s, 13)
notes(s, "TF 支持度来自同一套先验网络，存在循环性，解释时需谨慎。")

# ---------------------------------------------------------------- 14 model
s = add_slide(prs)
header(s, "生物学模型：AD 中 DAM 亚群向稳态小胶质细胞发送的信号", None)

send = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.7),
                          Inches(3.3), Inches(4.3))
send.fill.solid(); send.fill.fore_color.rgb = RGBColor(0xF8, 0xE3, 0xDF)
send.line.color.rgb = RED; send.line.width = Pt(1.5)
textbox(s, 0.85, 1.85, 3.0, 0.4, "Sender：DAM 亚群", size=14, bold=True, color=RED)
textbox(s, 0.85, 2.35, 3.0, 3.4,
        "Inflam.DAM\nLipo.DAM\nRibo.DAM1/2\n\n"
        "分泌：LY86、IL1B、IL18、\nAPOE、GAS6、TNFRSF14",
        size=11, color=DARKGREY)

recv = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(9.3), Inches(1.7),
                          Inches(3.3), Inches(4.3))
recv.fill.solid(); recv.fill.fore_color.rgb = RGBColor(0xE1, 0xEC, 0xF6)
recv.line.color.rgb = BLUE; recv.line.width = Pt(1.5)
textbox(s, 9.45, 1.85, 3.0, 0.4, "Receiver：稳态小胶质", size=14, bold=True, color=BLUE)
textbox(s, 9.45, 2.35, 3.0, 3.4,
        "Homeos1/2/3\n\n受体：TGFBR1/2、\nTREM2、SORL1、\nAXL、MERTK、IL1RAP",
        size=11, color=DARKGREY)

arrows = [
    ("LY86 → TLR4（未注释）\n炎症/抗原提呈 ↑", 3.05, NAVY),
    ("TGFB1 → TGFBR1/2\n稳态程序 ↓", 3.85, BLUE),
    ("APOE → TREM2/SORL1\n脂质代谢 ↓", 4.65, GREEN),
    ("GAS6 → AXL/MERTK\n吞噬功能 ↓", 5.45, GREY),
]
for text, y, color in arrows:
    arr = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(4.25), Inches(y),
                             Inches(4.8), Inches(0.45))
    arr.fill.solid(); arr.fill.fore_color.rgb = color
    arr.line.fill.background()
    textbox(s, 4.25, y - 0.42, 4.9, 0.4, text, size=9.5, color=color,
            align=PP_ALIGN.CENTER)

textbox(s, 0.6, 6.25, 12.2, 0.7,
        "模型：AD 中 DAM 亚群扩增并释放炎症配体（LY86、IL1B/IL18），同时 TGF-β、APOE–TREM2、"
        "GAS6–AXL 等稳态/吞噬信号减弱，导致稳态小胶质细胞去抑制、向激活态转化。",
        size=11, color=DARKGREY)
footer(s, 14)
notes(s, "综合模型：炎症配体增强 + 稳态配体减弱，共同驱动小胶质细胞状态转换。")

# ---------------------------------------------------------------- 15 limitations
s = add_slide(prs)
header(s, "局限性与注意事项", None)
bullets(s, [
    ("批次/研究混杂：AD 与对照在不同研究的贡献不平衡（如 Leng 2021 全为 AD、Franjic 2022 全为对照），"
     "DE 未校正研究来源，建议 pseudobulk + 协变量做敏感性分析", 0),
    ("环境 RNA：NLGN1/NLGN4Y/NRXN1 等神经元黏附分子检出率仅 10–20%，"
     "很可能是 snRNA-seq 的环境污染，不宜作为主结论", 0),
    ("LR 网络覆盖：LY86 的受体 TLR4 未收录在 21122021 版 lr_network 中，"
     "因此配体-受体图中 LY86 无对应受体；CALM3、UXS1 等胞内蛋白也被误列为配体", 0),
    ("先验网络循环性：配体-靶基因与信号通路推断使用同一套网络，TF 支持度高属于预期", 0),
    ("统计功效：Homeos3 仅 711 cells，上调基因仅 17 个，相关结论仅供参考", 0),
    ("单细胞水平未做细胞比例校正：AD 中亚型构成改变可能放大/掩盖亚型内差异", 0),
], 0.65, 1.45, 12.1, 5.2, size=12.5)
footer(s, 15)
notes(s, "列清楚五类局限，便于答辩时主动说明。")

# ---------------------------------------------------------------- 16 conclusion
s = add_slide(prs)
header(s, "结论", None)
items = [
    ("①", "建立 7 亚型 × AD/对照的 NicheNet 流程", "每亚型独立 DE、配体活性、配体-靶基因、配体-受体与信号通路，输出 275 个文件"),
    ("②", "LY86（MD-2）是最稳健的共享上调配体", "4/7 亚型排名第一，指向 TLR4 相关先天免疫激活"),
    ("③", "TGFB1 是下调方向的核心配体", "4/7 亚型排名第一，提示稳态 TGF-β 信号减弱"),
    ("④", "亚型特异信号清晰", "Homeos2：IL18/IL1B；Lipo.DAM：TNFRSF14/APOE–TREM2；Ribo：GAS6–AXL/MERTK"),
    ("⑤", "可直接用于文章的结果", "配体活性表、配体-靶基因表、LR 对、Circos、三色热图与信号边表"),
]
y = 1.45
for num, head, sub in items:
    textbox(s, 0.7, y, 0.6, 0.45, num, size=18, bold=True, color=LIGHTBLUE)
    textbox(s, 1.35, y - 0.03, 11.4, 0.4, head, size=15, bold=True, color=NAVY)
    textbox(s, 1.35, y + 0.36, 11.4, 0.45, sub, size=11, color=GREY)
    y += 1.02
footer(s, 16)
notes(s, "五条结论，对应前面的图。")

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
