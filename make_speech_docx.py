# -*- coding: utf-8 -*-
"""Build a simple Chinese speaker script (DOCX) for the 24-slide deck."""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.join(r"C:\Users\lenovo\Desktop\nichenet_data",
                   "NicheNet_7subtypes_讲解稿.docx")
NAVY = RGBColor(0x1B, 0x2A, 0x5B)
GREY = RGBColor(0x55, 0x55, 0x55)

doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(2.0)
sec.left_margin = Cm(2.3); sec.right_margin = Cm(2.3)

style = doc.styles["Normal"]
style.font.name = "微软雅黑"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.space_after = Pt(6)


def set_cn(run, size=10.5, bold=False, color=None):
    run.font.name = "微软雅黑"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def title_block():
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18); p.paragraph_format.space_after = Pt(2)
    r = p.add_run("NicheNet 7 亚型分析 · 汇报讲解稿")
    set_cn(r, size=18, bold=True, color=NAVY)
    p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p2.add_run("配套 PPT：NicheNet_7subtypes_AD_full_report.pptx（24 页）｜全程约 12–13 分钟")
    set_cn(r, size=9.5, color=GREY)


def h(text, size=12.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(3)
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr"); bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single"); bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:color"), "2C7FB8"); bdr.append(bottom); pPr.append(bdr)
    r = p.add_run(text)
    set_cn(r, size=size, bold=True, color=NAVY)


def body(text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0.74)
    r = p.add_run(text)
    set_cn(r, size=11)
    return p


def tip(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    set_cn(r, size=9.5, color=GREY)
    r.font.italic = True
    return p


def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def table(rows, widths, font_size=9):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if j else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(val))
            set_cn(r, size=font_size, bold=(i == 0))
            if i == 0:
                shade(cell, "1B2A5B")
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    for j, w in enumerate(widths):
        for row in t.rows:
            row.cells[j].width = Cm(w)
    # 同步 tblGrid，否则 LibreOffice/Word 仍按等宽渲染
    grid = t._tbl.tblGrid
    for j, w in enumerate(widths):
        grid.gridCol_lst[j].set(qn("w:w"), str(int(w / 2.54 * 1440)))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


title_block()

# ---------------------------------------------------------------- timing
h("一、时间分配（可按需删减）")
table([
    ["部分", "页码", "内容", "建议时长"],
    ["开场", "1–2", "封面 + 提纲", "40 秒"],
    ["背景与设计", "3–7", "科学问题、数据、设计、流程、参数", "3 分钟"],
    ["结果", "8–18", "DE、配体活性、关键配体、亚型特异、下游图", "6 分钟"],
    ["解读", "19–20", "生物学模型 + 文献对照", "1.5 分钟"],
    ["收尾", "21–24", "局限、结论、附录、致谢", "1.5 分钟"],
], [3.2, 2.0, 8.6, 2.6], font_size=9)
tip("提示：如果只给 8 分钟，可跳过第 9、15、17、18、23 页，其余照讲。")

# ---------------------------------------------------------------- script
h("二、逐页讲解稿")

slides = [
    ("第 1 页｜封面｜约 20 秒",
     "各位老师好，我汇报的题目是“AD 脑内小胶质细胞亚型间通讯的 NicheNet 分析”。我们用一套整合的单核转录组数据，"
     "把 7 个小胶质细胞亚型逐一作为接收细胞，看 AD 和对照之间哪些配体能够解释它们的转录改变。汇报分方法、结果和解读三部分。"),

    ("第 2 页｜提纲｜约 15 秒",
     "汇报按六块展开：背景与问题、数据与设计、方法与参数、五组结果、生物学解读，最后是局限和结论。"),

    ("第 3 页｜背景｜约 40 秒",
     "为什么做这件事。单细胞图谱已经把 AD 脑内的小胶质细胞分成稳态、炎症型 DAM、脂质型 DAM、核糖体型 DAM 等状态；"
     "AD 里 DAM 亚群扩增、稳态亚群减少，但“谁在调控谁”并不清楚。NicheNet 正好能回答：哪些配体能够解释接收细胞的转录变化。"
     "所以我们要看两件事：一是 AD 中哪些配体驱动了小胶质细胞的改变，二是这些配体来自哪个亚型、通过什么受体起作用。"),

    ("第 4 页｜数据｜约 40 秒",
     "数据是 scRNA.RData，61,388 个基因、48,347 个细胞。按之前商定的方案去掉了 DIMs 和 MAC 巨噬细胞，只保留 7 个亚群，"
     "一共 38,664 个细胞，分成 AD 和 No Neuropathology 两组。右边是每个亚型的细胞数。需要提醒的是 Homeos3 只有 711 个细胞，"
     "统计功效有限，后面还会提到。"),

    ("第 5 页｜设计｜约 50 秒",
     "这是整个分析最关键的设计。我们没有做亚型之间的 marker 比较，而是让每个亚型轮流当 receiver，只在这个亚型内部比较 AD 和对照，"
     "sender 始终是 7 个亚群全部，允许自分泌。原因是：AD 里亚型构成会变化，如果混在一起比，很容易把“比例变化”误当成“表达变化”。"
     "逐个亚型做就能避开这个问题，7 个亚型一共跑 7 轮。"),

    ("第 6 页｜流程｜约 30 秒",
     "每一轮五步：先做亚型内差异分析，再用 NicheNet 预测配体活性，然后做配体到靶基因的调控潜力、配体到受体的网络，"
     "最后推断从配体经受体、信号中介、转录因子到靶基因的通路。每一步的输出都存成表或图，可以追溯。"),

    ("第 7 页｜参数｜约 30 秒",
     "参数都固定在脚本里。差异分析用 Wilcoxon，padj 小于 0.05、log2FC 绝对值大于 0.25、两组检出率都到 10%，再按 logFC 取前 200 个基因。"
     "配体活性用 predict_ligand_activities，候选配体是 sender 表达、且在配体-受体网络里的 170 个；先验网络用的是 21122021 版本。"),

    ("第 8 页｜DE 结果｜约 40 秒",
     "这是各亚型的差异基因数。DAM 亚群最多，Inflam.DAM 有 2,627 个，Homeos1 有 2,909 个；稳态的 Homeos2 和 Homeos3 分别只有 1,091 和 143 个。"
     "最右两列是每个亚型排第一的上调和下调配体。这里要注意 Homeos3：上调基因只有 17 个，少于 20 个的阈值，配体活性被自动跳过了，"
     "所以它在上调的汇总图里没有列。"),

    ("第 9 页｜DE 解读｜约 30 秒",
     "从这张表可以得出一个策略上的结论：AD 的主要转录扰动发生在 DAM 亚群内部，稳态亚群变化更细微。所以与其问“DAM 自己怎么变”，"
     "不如问“DAM 给稳态小胶质细胞发送了什么信号”，这正是后面 7 轮设计的出发点。"),

    ("第 10 页｜上调配体活性｜约 40 秒",
     "这是跨亚型的配体活性汇总，上调方向。每行一个配体，每列一个 receiver，颜色越深活性越高。可以看到 LY86 在 4 个亚型里都排第一，"
     "NLGN1 在 Inflam.DAM 第一，IL18 在 Homeos2 第一；HLA-F、HLA-DMA、CD14、B2M 这些抗原提呈和髓系活化的配体也反复出现。"
     "这里只有 6 列，还是因为 Homeos3 上调基因不足。"),

    ("第 11 页｜下调配体活性｜约 40 秒",
     "下调方向这张是 7 列，Homeos3 在里面。最明显的是 TGFB1，在 4 个亚型里排第一；IL1B 在 Homeos2、TNFRSF14 在 Lipo.DAM、"
     "CALM3 在 Ribo.DAM2 是亚型特异的。APOE、GAS6、ENG、RECK 反复出现，指向脂质代谢和吞噬。整体上下调方向的活性比上调低，"
     "符合“信号减弱”而不是“新信号出现”。"),

    ("第 12 页｜LY86｜约 50 秒",
     "第一个关键发现是 LY86。它编码 MD-2，是 TLR4 的共受体，负责识别 LPS 和內源性损伤信号。在 Homeos1 里活性是 0.159，"
     "第二名 NLGN1 只有 0.099，差距很明显；在 Lipo.DAM、Ribo.DAM1、Ribo.DAM2 里也都是第一。它的靶基因集中在 HLA-DMA、CD14、B2M "
     "这些炎症和抗原提呈基因上。这里有个限制要说明：21122021 版网络里没有 LY86 和 TLR4 的注释，所以后面的 Circos 和配体-受体图里 "
     "LY86 没有对应受体，这是网络覆盖问题，不是分析遗漏。"),

    ("第 13 页｜TGFB1｜约 50 秒",
     "第二个关键发现是 TGFB1，出现在下调方向。它的靶基因在 AD 里整体下调，说明这条通路的转录程序被抑制了；受体 TGFBR1、TGFBR2、ENG "
     "在接收细胞里都有表达。TGF-β 是维持小胶质细胞稳态、抑制过度激活的关键因子，所以这个结果和“DAM 扩增、稳态亚群减少”的表型是一致的："
     "稳态信号减弱，细胞就被去抑制了。这是可以验证的假设，比如看 SMAD2/3 磷酸化或者通路评分。"),

    ("第 14 页｜亚型特异｜约 40 秒",
     "这张表把 7 个亚型的 top 配体、受体和可能的生物学过程放在一起。共性是 DAM 亚群普遍用 TGF-β 和吞噬相关的配体，比如 GAS6 到 AXL/MERTK、"
     "APOE 到 TREM2；差异主要在 IL-1/IL-18 和 TNFRSF14 上。Homeos2 是唯一以 IL18 和 IL1B 为主的亚型。"),

    ("第 15 页｜配体-靶基因｜约 30 秒",
     "这一页是配体到靶基因的调控潜力热图，以 Homeos1 上调方向为例。LY86 的靶基因包括 HLA-DMA、CD14、B2M；IL18 和 IL1B 共享 NFKBIA、SAT1，"
     "提示 NF-κB。这个矩阵是后面配体-受体和信号通路分析的输入。"),

    ("第 16 页｜配体-受体｜约 40 秒",
     "配体-受体有两个视角。左边 Circos 看“谁和谁配对”，配体按表达最高的亚型着色；右边是配体-受体层面的 logFC，展示 Lipo.DAM 里 "
     "HLA-DMA 到 CD74、CD14 到 PLXND1 这些配体或受体在 AD 里上调。这一页回答“信号由谁接收”。"),

    ("第 17 页｜LFC 三色热图｜约 35 秒",
     "这张三色热图把配体的变化定位到具体 sender 亚型：蓝色是 AD 中下调，红色是上调。HLA-DMA 在 Inflam.DAM 里强烈上调，CD14 在多个亚型上调；"
     "NLGN4Y、NLGN1 反而下调。要提醒的是，NLGN1 这类神经元黏附分子检出率只有十几个百分点，很可能是环境 RNA，不适合作为主要结论。"),

    ("第 18 页｜TF 支持度｜约 35 秒",
     "最后一张结果图是配体-靶基因链接的转录因子支持度。我们沿着配体、受体、信号、转录因子、靶基因推断路径，统计每条链接有多少个转录因子支持，"
     "颜色越深支持越多。需要说明：配体-靶基因预测和通路推断用的是同一套先验网络，所以支持度普遍偏高，这张图更适合作为一致性检查，"
     "而不是独立证据。"),

    ("第 19 页｜生物学模型｜约 45 秒",
     "把结果合起来就是这张模型图。AD 里 DAM 亚群扩增，释放 LY86、IL1B、IL18 这些炎症配体，通过 TLR4 和 IL-1 受体增强炎症输入；"
     "同时 TGFB1 的稳态信号、APOE 到 TREM2 的脂质信号、GAS6 到 AXL/MERTK 的吞噬信号都在减弱。一增一减，稳态小胶质细胞被去抑制，"
     "向激活态转化。"),

    ("第 20 页｜文献对照｜约 30 秒",
     "这张表把结果和已知 AD 机制对照：APOE-TREM2 是 AD 最强的遗传风险轴，TGF-β 维持稳态，TLR4/MD-2 识别 Aβ，GAS6-AXL/MERTK 清除凋亡细胞，"
     "IL-1β/IL-18 来自 NLRP3 炎症小体。方向和文献一致，但这只支持可信度，不能替代功能实验。"),

    ("第 21 页｜局限｜约 40 秒",
     "局限有六点。最重要的是研究批次混杂：AD 和对照在不同研究里的贡献不平衡，我们没有校正研究来源，建议后续用 pseudobulk 加协变量做敏感性分析。"
     "其次是环境 RNA、网络注释不全、先验网络的循环性、Homeos3 样本量小，以及没有做细胞比例校正。这些在文章里都要写清楚。"),

    ("第 22 页｜结论｜约 40 秒",
     "结论五条：第一，建立了 7 个亚型各跑一次的 NicheNet 流程，输出 275 个文件；第二，LY86 是最稳健的共享上调配体，指向 TLR4；"
     "第三，TGFB1 是下调方向的核心配体，提示稳态信号减弱；第四，亚型特异信号清晰；第五，这些表和图可以直接用于文章。"),

    ("第 23 页｜附录｜约 15 秒",
     "附录是文件清单和复现方式，脚本、结果目录和 12 类图的编号都写在里面，需要时可以直接查。"),

    ("第 24 页｜结束｜约 15 秒",
     "我的汇报到这里，谢谢各位老师，欢迎提问。"),
]

for head, text in slides:
    h(head)
    body(text)

# ---------------------------------------------------------------- Q&A
h("三、可能被问到的问题（备用）")
qa = [
    ("为什么不做亚型之间的比较？",
     "亚型构成在 AD 里会变化，混在一起比较会把比例变化误判成表达变化。逐个亚型内部比较，才能干净地回答“这个亚型自己发生了什么”。"),
    ("Homeos3 为什么没有上调结果？",
     "它只有 711 个细胞，上调基因只有 17 个，少于配体活性要求的 20 个基因，所以被跳过；下调方向有 89 个基因，正常参与。"),
    ("LY86 为什么没有对应的受体？",
     "21122021 版配体-受体网络没有收录 LY86–TLR4 这一对；配体活性本身不依赖受体，所以 LY86 仍然可以排第一，但下游的配体-受体图会缺这一条。"),
    ("配体活性 0.1 算高吗？",
     "NicheNet 的 Pearson 一般在 0.05–0.3 之间，绝对值受基因集大小影响，更重要的是同一亚型内的相对排序，以及跨亚型是否一致。"),
    ("这些结果能说明因果吗？",
     "不能。NicheNet 是基于先验网络和转录组的相关性推断，只能提出假设，需要通路评分、配体中和或共培养实验验证。"),
]
for q, a in qa:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("Q：" + q)
    set_cn(r, size=10.5, bold=True, color=NAVY)
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(8)
    p2.paragraph_format.left_indent = Cm(0.6)
    r2 = p2.add_run("A：" + a)
    set_cn(r2, size=10.5)

h("四、讲的时候的三个小提醒")
body("第一，第 5 页的设计和第 8 页的 Homeos3 说明一定要讲清楚，这两处最容易被追问。")
body("第二，讲配体时先说“相对排序”，再说具体数值，避免把 0.159 这种绝对值当成效应量。")
body("第三，第 12、13 页各留一句“这是假设，需要验证”，会显得更稳。")

doc.save(OUT)
print("saved", OUT)
