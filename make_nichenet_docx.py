# -*- coding: utf-8 -*-
"""Build the NicheNet analysis report (Chinese DOCX)."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                    "NicheNet_results_7subtypes", "20261031_1842")
OUT = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                   "NicheNet_7subtypes_AD_analysis.docx")

NAVY = RGBColor(0x1B, 0x2A, 0x5B)
GREY = RGBColor(0x55, 0x55, 0x55)

doc = Document()

# page + base style
sec = doc.sections[0]
sec.top_margin = Cm(2.2)
sec.bottom_margin = Cm(2.2)
sec.left_margin = Cm(2.4)
sec.right_margin = Cm(2.4)

style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
style.paragraph_format.line_spacing = 1.4
style.paragraph_format.space_after = Pt(6)


def set_cn(run, size=10.5, bold=False, color=None, font="微软雅黑"):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def heading(text, level=1):
    sizes = {1: 16, 2: 13, 3: 11.5}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_cn(run, size=sizes[level], bold=True, color=NAVY)
    if level == 1:
        pPr = p._p.get_or_add_pPr()
        border = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "8")
        bottom.set(qn("w:color"), "2C7FB8")
        border.append(bottom)
        pPr.append(border)
    return p


def para(text, size=10.5, color=None, italic=False, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    set_cn(run, size=size, color=color)
    run.font.italic = italic
    return p


def bullet(text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    set_cn(run, size=size)
    return p


def figure(path, caption, width_cm=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(path, width=Cm(width_cm))
    c = doc.add_paragraph()
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    c.paragraph_format.space_after = Pt(10)
    run = c.add_run(caption)
    set_cn(run, size=9, color=GREY)


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_table(rows, widths=None, font_size=9):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j > 0 else WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(str(val))
            set_cn(run, size=font_size, bold=(i == 0))
            if i == 0:
                shade(cell, "1B2A5B")
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    if widths:
        for j, w in enumerate(widths):
            for row in table.rows:
                row.cells[j].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


# ------------------------------------------------------------------ title
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.paragraph_format.space_before = Pt(30)
r = t.add_run("AD 小胶质细胞 7 个亚型的 NicheNet 细胞通讯分析")
set_cn(r, size=18, bold=True, color=NAVY)

st = doc.add_paragraph()
st.alignment = WD_ALIGN_PARAGRAPH.CENTER
st.paragraph_format.space_after = Pt(4)
r = st.add_run("配体活性 · 配体–靶基因 · 配体–受体 · 信号通路")
set_cn(r, size=11, color=GREY)

st2 = doc.add_paragraph()
st2.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = st2.add_run("数据：scRNA.RData（48,347 cells；去除 DIMs / MAC 后 38,664 cells）\n"
                "结果目录：NicheNet_results_7subtypes/20261031_1842　｜　2026-11-01")
set_cn(r, size=9.5, color=GREY)

# ------------------------------------------------------------------ 1
heading("1　数据与分析方法")
para("分析对象为整合的人类小胶质细胞单细胞/单核转录组图谱 scRNA（61,388 genes × 48,347 cells）。"
     "按既定方案剔除 DIMs 与 MAC（巨噬细胞）后保留 7 个亚群：Homeos1、Homeos2、Homeos3、"
     "Inflam.DAM、Lipo.DAM、Ribo.DAM1、Ribo.DAM2，共 38,664 个细胞；分组为 AD 与 No Neuropathology。")
para("分析采用“每个亚型各当一次 receiver”的设计：对亚型 i，仅用该亚型细胞做 AD vs 对照差异分析"
     "（FindMarkers，Wilcoxon，padj < 0.05、|log2FC| ≥ 0.25、两组检出率 ≥ 10%、剔除 MT- 基因），"
     "上调/下调各取 top 200 个基因作为 NicheNet 的 gene set；sender 为 7 个亚群全部（含自分泌）。"
     "配体活性用 predict_ligand_activities 计算（Pearson 与 AUPR），背景为该 receiver 表达且存在于"
     "先验矩阵中的基因。")

rows = [
    ["亚型", "细胞数", "AD", "对照", "显著 DE", "上调基因集", "下调基因集"],
    ["Homeos1", "12,775", "5,162", "7,613", "2,909", "200", "200"],
    ["Homeos2", "4,582", "1,748", "2,834", "1,091", "68", "200"],
    ["Homeos3", "711", "296", "415", "143", "17*", "89"],
    ["Inflam.DAM", "13,214", "6,066", "7,148", "2,627", "200", "200"],
    ["Lipo.DAM", "1,512", "881", "631", "1,127", "200", "200"],
    ["Ribo.DAM1", "4,307", "1,461", "2,846", "1,349", "200", "200"],
    ["Ribo.DAM2", "1,563", "668", "895", "492", "169", "200"],
]
add_table(rows, widths=[2.4, 2.0, 1.8, 1.8, 2.0, 2.4, 2.4], font_size=8.5)
para("* Homeos3 上调基因仅 17 个（< 20），配体活性分析自动跳过。", size=9, color=GREY, italic=True)

# ------------------------------------------------------------------ 2
heading("2　主要结果")
heading("2.1　AD 的转录扰动主要集中在 DAM 亚群", 2)
para("显著差异基因数从 143（Homeos3，仅 711 cells）到 2,909（Homeos1）不等。"
     "三个 DAM 亚群（Inflam.DAM 2,627、Ribo.DAM1 1,349、Lipo.DAM 1,127）均检出大量差异基因，"
     "而稳态亚群 Homeos2/3 的差异基因明显更少。这提示 AD 的转录变化主要发生在激活态亚群内部，"
     "稳态亚群更适合作为“接收方”来评估外部信号的影响。")

heading("2.2　配体活性：上调以 LY86 为首，下调以 TGFB1 为首", 2)
para("跨 7 个 receiver 的配体活性汇总显示两个高度一致的信号：")
bullet("LY86 在 Homeos1、Lipo.DAM、Ribo.DAM1、Ribo.DAM2 四个亚型的上调方向均排名第一"
       "（Homeos1 中 Pearson = 0.159，第二名 NLGN1 为 0.099），在 Inflam.DAM 中排名第二。")
bullet("TGFB1 在 Homeos1、Homeos3、Inflam.DAM、Ribo.DAM1 四个亚型的下调方向均排名第一"
       "（Pearson 0.064–0.096），其受体 TGFBR1、TGFBR2、ENG 在 receiver 中均有表达。")
bullet("APOE（受体 TREM2 / SORL1 / LRP1）、GAS6（受体 AXL / MERTK）、ENG、RECK 在多个亚型反复出现，"
       "指向脂质代谢与吞噬通路。")

figure(os.path.join(BASE, "SUMMARY_ligand_activity_heatmap_up.png"),
       "图 1　跨 7 个亚型的配体活性热图（上调基因）。行 = 配体，列 = receiver 亚型，颜色 = Pearson 活性。", 12.5)
figure(os.path.join(BASE, "receiver_Homeos1", "01_ligand_activity_bar_up.png"),
       "图 2　Homeos1（上调方向）优先配体排序。LY86 显著领先，其后为 NLGN1、TF、NLGN4Y、JAM2。", 10.5)

heading("2.3　配体–靶基因：炎症与抗原提呈模块", 2)
para("以 Homeos1 上调方向为例，LY86 的预测靶基因包括 HLA-DMA、CD14、B2M 等抗原提呈与髓系活化基因；"
     "IL18/IL1B 则共享 NFKBIA、SAT1 等下游靶基因，提示 NF-κB 通路。配体–靶基因调控潜力矩阵"
     "（03_ligand_target_heatmap_*）是后续配体–受体与信号通路分析的输入。")

heading("2.4　配体–受体：谁在接收信号", 2)
para("配体–受体热图与 Circos 图显示，DAM 来源的配体主要通过 TGFBR1/2、ENG、TREM2、SORL1、"
     "AXL/MERTK、IL1RAP 等受体作用于接收细胞。配体–受体 LFC 图进一步显示，在 Lipo.DAM 中 "
     "HLA-DMA–CD74、CD14–PLXND1 等配体/受体对在 AD 中上调。需要说明的是，LY86 的受体 TLR4 "
     "未被 21122021 版 lr_network 收录，因此 Circos 与 LR 热图中 LY86 没有对应受体。")
figure(os.path.join(BASE, "receiver_Lipo.DAM", "11_ligand_receptor_lfc_up.png"),
       "图 3　Lipo.DAM（上调方向）配体–受体 LFC 图。左：配体在 sender 中的 LFC；右：受体在 receiver 中的 LFC。", 16)

heading("2.5　信号通路：TF 支持度", 2)
para("沿 ligand→受体→信号中介→TF→靶基因 推断路径，统计每条配体–靶基因链接由多少个 TF 支持。"
     "Homeos1 上调方向 75 条链接全部获得 TF 支持（多为 20–30 个 TF）。由于配体–靶基因预测与"
     "信号通路推断使用同一套先验网络，该结果更适合作为通路一致性检查，而不是独立证据。")

heading("2.6　亚型特异信号", 2)
rows2 = [
    ["receiver", "top 上调配体", "top 下调配体", "主要受体", "可能过程"],
    ["Homeos1", "LY86 / NLGN1", "TGFB1 / APOE", "TGFBR1/2, TREM2, SORL1", "稳态维持、脂质代谢"],
    ["Homeos2", "IL18 / JAM2", "IL1B / TGFB1", "IL1RAP, IL1RAPL1", "炎症小体、IL-1 家族"],
    ["Homeos3", "—（基因不足）", "TGFB1 / TIMP1", "TGFBR1/2, CD63", "基质重塑（样本量小）"],
    ["Inflam.DAM", "NLGN1 / LY86", "TGFB1 / ENG", "TGFBR1/2, ENG", "炎症活化、血管生成"],
    ["Lipo.DAM", "LY86 / NLGN1", "TNFRSF14 / APOE", "TREM2, SORL1, LRP1", "脂质处理、吞噬"],
    ["Ribo.DAM1", "LY86 / NLGN1", "TGFB1 / GAS6", "TGFBR1/2, AXL, MERTK", "核糖体应激、吞噬"],
    ["Ribo.DAM2", "LY86 / TF", "CALM3 / GAS6", "AXL, MERTK", "钙信号、吞噬"],
]
add_table(rows2, widths=[2.2, 3.0, 3.0, 3.6, 3.6], font_size=8)

# ------------------------------------------------------------------ 3
heading("3　生物学解读")
para("综合上述结果，AD 中 DAM 亚群与稳态小胶质细胞之间呈现“炎症信号增强 + 稳态信号减弱”的双向改变：")
bullet("炎症输入增强：LY86（MD-2，TLR4 共受体）是上调方向最稳健的共享配体，其靶基因富集于 "
       "HLA-DMA、CD14、B2M 等抗原提呈与髓系活化基因；IL18/IL1B 在 Homeos2 中居首，提示炎症小体–IL-1 轴。")
bullet("稳态信号减弱：TGFB1 的靶基因在 AD 中整体下调，提示 TGF-β 稳态程序受抑；"
       "APOE–TREM2/SORL1 与 GAS6–AXL/MERTK 的靶基因同样偏向下调，提示脂质处理与吞噬功能受损。")
bullet("亚型特异：Lipo.DAM 以 TNFRSF14、APOE 为主，与其脂质处理表型一致；"
       "Ribo.DAM1/2 以 GAS6、RECK 为主，指向吞噬与基质重塑。")
para("据此可提出可检验的假设：AD 中 DAM 亚群扩增并释放炎症配体（LY86、IL1B/IL18），"
     "同时 TGF-β、APOE–TREM2、GAS6–AXL 等稳态/吞噬信号减弱，使稳态小胶质细胞去抑制并向激活态转化。")

# ------------------------------------------------------------------ 4
heading("4　局限与注意事项")
bullet("批次/研究混杂：AD 与对照在不同研究的贡献不平衡（如 Leng 2021 全为 AD、Franjic 2022 全为对照），"
       "DE 未校正研究来源；建议用 pseudobulk + 研究作为协变量做敏感性分析。")
bullet("环境 RNA：NLGN1、NLGN4Y、NRXN1 等神经元黏附分子在微胶质中检出率仅 10–20%，"
       "很可能是 snRNA-seq 的环境污染，不宜作为主要结论。")
bullet("先验网络覆盖与注释误差：LY86 的受体 TLR4 未收录；CALM3、UXS1 等胞内蛋白被数据库列为配体，"
       "解释时需谨慎。")
bullet("网络循环性：配体–靶基因与信号通路推断共用同一套网络，TF 支持度高属于预期。")
bullet("统计功效：Homeos3 仅 711 cells，上调基因仅 17 个，相关结论仅供参考。")

# ------------------------------------------------------------------ 5
heading("5　结论")
para("① 建立了 7 亚型 × AD/对照的 NicheNet 流程，每个亚型独立完成 DE、配体活性、配体–靶基因、"
     "配体–受体与信号通路分析，合计输出 275 个文件。")
para("② LY86（MD-2）是上调方向最稳健的共享配体（4/7 亚型第一），指向 TLR4 相关先天免疫激活。")
para("③ TGFB1 是下调方向的核心配体（4/7 亚型第一），提示稳态 TGF-β 信号减弱。")
para("④ 亚型特异信号清晰：Homeos2 的 IL18/IL1B、Lipo.DAM 的 TNFRSF14 与 APOE–TREM2、"
     "Ribo 亚群的 GAS6–AXL/MERTK。")

heading("附　结果文件说明")
para("每个 receiver 目录（receiver_XXX/）含 12 类图与 9 张表，主要包括：01 配体活性条形图、"
     "02 直方图、03 配体–靶基因热图、04 配体–受体热图、05 配体表达 DotPlot、06 靶基因表达热图、"
     "07 Circos、08 小提琴图、09 配体 LFC 三色热图、10 活性–表达–LFC–靶基因组合图、"
     "11 配体–受体 LFC、12 信号通路 TF 支持热图，以及 DE 表、基因集、配体活性表、"
     "配体–靶基因表、LR 对表与 signaling 边表（可导入 Cytoscape）。", size=9.5)

doc.save(OUT)
print("saved", OUT)
