import io
from datetime import date

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle

st.set_page_config(page_title="HADAOJI PRINT 見積・請求", page_icon="🧾", layout="centered")

BODY_MASTER = {
    "00085-CVT": {
        "name": "TOMS 00085-CVT 5.6oz Tシャツ",
        "variants": {
            "100〜150": {"sell": 600, "cost": 400},
            "WM〜XL": {"sell": 660, "cost": 440},
            "XXL〜XXXL": {"sell": 840, "cost": 560},
            "4XL〜5XL": {"sell": 960, "cost": 640},
        },
    },
    "00300-ACT": {
        "name": "TOMS 00300-ACT ドライTシャツ",
        "variants": {
            "100〜150": {"sell": 480, "cost": 320},
            "WM〜LL": {"sell": 516, "cost": 344},
            "3L〜5L": {"sell": 594, "cost": 396},
            "6L〜7L": {"sell": 810, "cost": 540},
        },
    },
    "5001-01": {
        "name": "United Athle 5001-01 Tシャツ",
        "variants": {
            "S〜XL ホワイト": {"sell": 756, "cost": 504},
            "S〜XL カラー": {"sell": 816, "cost": 544},
            "XXL ホワイト": {"sell": 948, "cost": 632},
            "XXL カラー": {"sell": 1020, "cost": 680},
            "XXXL ホワイト": {"sell": 1092, "cost": 728},
            "XXXL カラー": {"sell": 1152, "cost": 768},
        },
    },
    "5001-02": {
        "name": "United Athle 5001-02 キッズTシャツ",
        "variants": {
            "90〜160 ホワイト": {"sell": 690, "cost": 460},
            "90〜160 カラー": {"sell": 744, "cost": 496},
        },
    },
    "5011-01": {
        "name": "United Athle 5011-01 ロングスリーブTシャツ",
        "variants": {
            "S〜XL ホワイト": {"sell": 1188, "cost": 792},
            "S〜XL カラー": {"sell": 1320, "cost": 880},
            "XXL ホワイト": {"sell": 1392, "cost": 928},
            "XXL カラー": {"sell": 1560, "cost": 1040},
        },
    },
    "持ち込み": {
        "name": "持ち込みウェア",
        "variants": {"持ち込み": {"sell": 0, "cost": 0}},
    },
}

BANK_INFO = "PayPay銀行　ビジネス営業部（005）\n普通 7546092\n株式会社ハダオジ（カ）ハダオジ）"
COMPANY_INFO = "株式会社ハダオジ\nHADAOJI PRINT\nhadaojiprint.base.shop"


def yen(v):
    return f"{int(round(v)):,}円"


def get_print_unit(qty, special=False):
    if qty <= 9:
        sell, cost = 800, 500
    elif qty >= 100:
        sell, cost = 200, 100
    else:
        sell, cost = 300, 150
    if special:
        sell += 150
        cost += 100
    return sell, cost


def make_pdf(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note, show_bank=True):
    buf = io.BytesIO()
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=14*mm, leftMargin=14*mm, topMargin=12*mm, bottomMargin=12*mm)

    normal = ParagraphStyle("normal", fontName="HeiseiKakuGo-W5", fontSize=9, leading=13)
    small = ParagraphStyle("small", fontName="HeiseiKakuGo-W5", fontSize=8, leading=11)
    title = ParagraphStyle("title", fontName="HeiseiKakuGo-W5", fontSize=22, leading=28, alignment=1)
    logo = ParagraphStyle("logo", fontName="HeiseiKakuGo-W5", fontSize=16, leading=18, alignment=2)
    amount_label = "御見積金額（税込）" if doc_type == "見積書" else "御請求金額（税込）"

    story = []
    story.append(Paragraph(doc_type, title))
    story.append(Spacer(1, 5))

    header = Table([
        [Paragraph(f"<b>{customer}</b><br/><br/>下記の通りご提出いたします。", normal),
         Paragraph("<b>HADAOJI PRINT</b><br/>WE PRINT YOUR WAY!<br/><br/>" + COMPANY_INFO.replace("\n", "<br/>"), logo)]
    ], colWidths=[100*mm, 78*mm])
    header.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
    ]))
    story.append(header)
    story.append(Spacer(1, 8))

    meta = Table([
        ["件名", subject, "番号", quote_no],
        ["発行日", date.today().strftime("%Y/%m/%d"), "有効期限", "発行日より30日"],
    ], colWidths=[22*mm, 82*mm, 22*mm, 52*mm])
    meta.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "HeiseiKakuGo-W5"),
        ("GRID", (0,0), (-1,-1), 0.6, colors.black),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
        ("BACKGROUND", (2,0), (2,-1), colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(meta)
    story.append(Spacer(1, 10))

    amount = Table([[Paragraph(f"<b>{amount_label}</b>", normal), Paragraph(f"<font size='24'><b>{yen(total)}</b></font>", normal)]], colWidths=[70*mm, 108*mm])
    amount.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 2.2, colors.black),
        ("BACKGROUND", (0,0), (-1,-1), colors.whitesmoke),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(amount)
    story.append(Spacer(1, 12))

    data = [["品目", "内容", "数量", "単価", "金額"]]
    for r in rows:
        data.append([r["item"], r["desc"], r["qty"], yen(r["unit"]), yen(r["amount"])])
    data += [["", "", "", "小計", yen(subtotal)], ["", "", "", "消費税10%", yen(tax)], ["", "", "", "合計", yen(total)]]

    table = Table(data, colWidths=[45*mm, 58*mm, 24*mm, 25*mm, 26*mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "HeiseiKakuGo-W5"),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (2,1), (-1,-1), "RIGHT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    note_text = note.replace("\n", "<br/>") if note else "納期・仕様はご注文確定後に確認いたします。"
    note_tbl = Table([[Paragraph("<b>備考</b>", normal)], [Paragraph(note_text, small)]], colWidths=[178*mm], rowHeights=[8*mm, 28*mm])
    note_tbl.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "HeiseiKakuGo-W5"),
        ("BOX", (0,0), (-1,-1), 0.8, colors.black),
        ("BACKGROUND", (0,0), (0,0), colors.lightgrey),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(note_tbl)

    if show_bank:
        story.append(Spacer(1, 8))
        story.append(Paragraph("<b>お振込先</b><br/>" + BANK_INFO.replace("\n", "<br/>"), small))

    doc.build(story)
    buf.seek(0)
    return buf


st.title("HADAOJI PRINT 見積・請求アプリ v2")
st.caption("正式レイアウトPDF対応")

with st.form("quote"):
    doc_type = st.selectbox("書類種類", ["見積書", "請求書"])
    quote_no = st.text_input("見積番号 / 請求番号", f"HP-{date.today().strftime('%Y%m%d')}-001")
    customer = st.text_input("宛名", "〇〇 様")
    subject = st.text_input("件名", "オリジナルウェア制作")

    st.subheader("ボディ")
    body_code = st.selectbox("品番", list(BODY_MASTER.keys()))
    variant = st.selectbox("区分", list(BODY_MASTER[body_code]["variants"].keys()))
    qty = st.number_input("枚数", min_value=1, value=10, step=1)
    manual_body = st.checkbox("ボディ単価を手入力する")
    default_sell = BODY_MASTER[body_code]["variants"][variant]["sell"]
    default_cost = BODY_MASTER[body_code]["variants"][variant]["cost"]
    body_sell = st.number_input("ボディ販売単価", min_value=0, value=default_sell, step=10, disabled=not manual_body)
    body_cost = st.number_input("ボディ原価", min_value=0, value=default_cost, step=10, disabled=not manual_body)

    st.subheader("プリント")
    print_spots = st.number_input("プリント箇所数", min_value=0, value=1, step=1)
    plate_count = st.number_input("製版数", min_value=0, value=1, step=1)
    special = st.checkbox("特色プリント（販売+150円 / 原価+100円）")
    show_bank = st.checkbox("振込先を表示", value=(doc_type == "請求書"))

    note = st.text_area("備考", "納期：約2週間\nデザイン・プリント内容確定後の制作開始となります。")
    submitted = st.form_submit_button("計算する")

print_unit_sell, print_unit_cost = get_print_unit(qty, special)
body_total = body_sell * qty
body_cost_total = body_cost * qty
print_total = print_unit_sell * qty * print_spots
print_cost_total = print_unit_cost * qty * print_spots
plate_total = 8000 * plate_count
plate_cost_total = 5500 * plate_count
subtotal = body_total + print_total + plate_total
tax = subtotal * 0.1
total = subtotal + tax
cost_total = body_cost_total + print_cost_total + plate_cost_total
profit = subtotal - cost_total

rows = []
rows.append({"item": "ボディ", "desc": f"{body_code} {BODY_MASTER[body_code]['name']} / {variant}", "qty": f"{qty}枚", "unit": body_sell, "amount": body_total})
if print_spots:
    rows.append({"item": "プリント代", "desc": f"{print_spots}箇所" + (" / 特色" if special else ""), "qty": f"{qty}枚", "unit": print_unit_sell * print_spots, "amount": print_total})
if plate_count:
    rows.append({"item": "製版代", "desc": "シルクスクリーン製版", "qty": f"{plate_count}版", "unit": 8000, "amount": plate_total})

st.subheader("計算結果")
c1, c2 = st.columns(2)
c1.metric("税込合計", yen(total))
c2.metric("利益", yen(profit))
st.caption(f"小計 {yen(subtotal)} / 消費税 {yen(tax)} / 原価 {yen(cost_total)}")

pdf = make_pdf(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note, show_bank)
st.download_button(
    "正式PDFをダウンロード",
    data=pdf,
    file_name=f"{quote_no}_{doc_type}.pdf",
    mime="application/pdf",
    type="primary",
)
