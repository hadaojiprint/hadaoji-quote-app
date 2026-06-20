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

st.set_page_config(page_title="HADAOJI PRINT 見積", page_icon="🧾", layout="wide")

DEFAULT_MASTER = {
    "00085-CVT": {"name":"5.6oz Tシャツ", "variants":{"100〜150":{"sell":600,"cost":400},"WM〜XL":{"sell":660,"cost":440},"XXL〜XXXL":{"sell":840,"cost":560},"4XL〜5XL":{"sell":960,"cost":640}}},
    "00300-ACT": {"name":"ドライTシャツ", "variants":{"100〜150":{"sell":480,"cost":320},"WM〜LL":{"sell":516,"cost":344},"3L〜5L":{"sell":594,"cost":396},"6L〜7L":{"sell":810,"cost":540}}},
    "5001-01": {"name":"United Athle Tシャツ", "variants":{"S〜XL ホワイト":{"sell":756,"cost":504},"S〜XL カラー":{"sell":816,"cost":544},"XXL カラー":{"sell":1020,"cost":680},"XXXL カラー":{"sell":1152,"cost":768}}},
    "5001-02": {"name":"United Athle キッズTシャツ", "variants":{"90〜160 ホワイト":{"sell":690,"cost":460},"90〜160 カラー":{"sell":744,"cost":496}}},
    "5011-01": {"name":"United Athle ロンT", "variants":{"S〜XL ホワイト":{"sell":1188,"cost":792},"S〜XL カラー":{"sell":1320,"cost":880},"XXL カラー":{"sell":1560,"cost":1040}}},
}

if "master" not in st.session_state:
    st.session_state.master = DEFAULT_MASTER.copy()
if "body_count" not in st.session_state:
    st.session_state.body_count = 1


def yen(v):
    return f"{int(round(v)):,}円"


def print_unit(qty, special):
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


def make_pdf(doc_type, no, customer, subject, rows, subtotal, tax, total, note):
    buf = io.BytesIO()
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=14*mm, leftMargin=14*mm, topMargin=14*mm, bottomMargin=14*mm)
    p = ParagraphStyle("p", fontName="HeiseiKakuGo-W5", fontSize=9, leading=13)
    title = ParagraphStyle("title", fontName="HeiseiKakuGo-W5", fontSize=22, leading=28, alignment=1)
    label = "御見積金額（税込）" if doc_type == "見積書" else "御請求金額（税込）"
    story = [Paragraph(doc_type, title), Spacer(1, 8)]
    story.append(Paragraph(f"<b>{customer}</b><br/>件名：{subject}<br/>番号：{no}<br/>発行日：{date.today().strftime('%Y/%m/%d')}<br/><br/><b>HADAOJI PRINT</b><br/>株式会社ハダオジ", p))
    story.append(Spacer(1, 8))
    amount = Table([[label, yen(total)]], colWidths=[70*mm, 100*mm])
    amount.setStyle(TableStyle([("BOX",(0,0),(-1,-1),2,colors.black),("BACKGROUND",(0,0),(-1,-1),colors.whitesmoke),("ALIGN",(1,0),(1,0),"RIGHT"),("FONTSIZE",(1,0),(1,0),20),("FONTNAME",(0,0),(-1,-1),"HeiseiKakuGo-W5"),("TOPPADDING",(0,0),(-1,-1),10),("BOTTOMPADDING",(0,0),(-1,-1),10)]))
    story += [amount, Spacer(1, 10)]
    data = [["品目", "内容", "数量", "単価", "金額"]]
    for r in rows:
        data.append([r["item"], r["desc"], r["qty"], yen(r["unit"]), yen(r["amount"])])
    data += [["", "", "", "小計", yen(subtotal)], ["", "", "", "消費税", yen(tax)], ["", "", "", "合計", yen(total)]]
    table = Table(data, colWidths=[35*mm, 70*mm, 22*mm, 28*mm, 28*mm])
    table.setStyle(TableStyle([("FONTNAME",(0,0),(-1,-1),"HeiseiKakuGo-W5"),("GRID",(0,0),(-1,-1),0.5,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("ALIGN",(2,1),(-1,-1),"RIGHT"),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [table, Spacer(1, 10), Paragraph("<b>備考</b><br/>" + note.replace("\n", "<br/>"), p)]
    doc.build(story)
    buf.seek(0)
    return buf


st.title("HADAOJI PRINT 見積・請求アプリ v4")
st.caption("複数ボディ・自由入力・簡易マスター登録対応")

with st.expander("マスター登録（この画面内で追加できます）"):
    m1, m2 = st.columns(2)
    with m1:
        new_code = st.text_input("品番", "")
        new_name = st.text_input("商品名", "")
    with m2:
        new_variant = st.text_input("区分・サイズ・色", "S〜XL カラー")
        new_sell = st.number_input("販売単価", 0, 99999, 0, key="new_sell")
        new_cost = st.number_input("原価", 0, 99999, 0, key="new_cost")
    if st.button("マスターに追加"):
        if new_code and new_name and new_variant:
            if new_code not in st.session_state.master:
                st.session_state.master[new_code] = {"name": new_name, "variants": {}}
            st.session_state.master[new_code]["name"] = new_name
            st.session_state.master[new_code]["variants"][new_variant] = {"sell": new_sell, "cost": new_cost}
            st.success(f"{new_code} を追加しました")
        else:
            st.warning("品番・商品名・区分を入力してください")

left, right = st.columns([1, 1.1])

with left:
    st.subheader("基本情報")
    doc_type = st.selectbox("書類種類", ["見積書", "請求書"])
    no = st.text_input("番号", f"HP-{date.today().strftime('%Y%m%d')}-001")
    customer = st.text_input("宛名", "〇〇 様")
    subject = st.text_input("件名", "オリジナルウェア制作")

    st.subheader("ボディ明細")
    c1, c2 = st.columns(2)
    if c1.button("＋ ボディ項目を増やす"):
        st.session_state.body_count += 1
    if c2.button("− 1行減らす") and st.session_state.body_count > 1:
        st.session_state.body_count -= 1

    body_rows = []
    for i in range(st.session_state.body_count):
        st.markdown(f"#### ボディ {i+1}")
        mode = st.selectbox("入力方法", ["マスターから選択", "自由入力"], key=f"mode_{i}")
        if mode == "マスターから選択":
            code = st.selectbox("品番", list(st.session_state.master.keys()), key=f"code_{i}")
            variant = st.selectbox("区分", list(st.session_state.master[code]["variants"].keys()), key=f"var_{i}")
            item_name = f"{code} {st.session_state.master[code]['name']} / {variant}"
            default_sell = st.session_state.master[code]["variants"][variant]["sell"]
            default_cost = st.session_state.master[code]["variants"][variant]["cost"]
            manual = st.checkbox("この行だけ単価を変更", key=f"manual_{i}")
            sell = st.number_input("販売単価", 0, 99999, default_sell, key=f"sell_{i}", disabled=not manual)
            cost = st.number_input("原価", 0, 99999, default_cost, key=f"cost_{i}", disabled=not manual)
        else:
            item_name = st.text_input("品番・商品名・色・サイズ", "未登録ボディ", key=f"free_name_{i}")
            sell = st.number_input("販売単価", 0, 99999, 0, key=f"free_sell_{i}")
            cost = st.number_input("原価", 0, 99999, 0, key=f"free_cost_{i}")
        qty = st.number_input("枚数", 1, 9999, 10, key=f"qty_{i}")
        body_rows.append({"name": item_name, "qty": qty, "sell": sell, "cost": cost})

    st.subheader("プリント")
    print_spots = st.number_input("プリント箇所数", 0, 10, 1)
    plate_count = st.number_input("製版数", 0, 10, 1)
    special = st.checkbox("特色プリント（販売+150円 / 原価+100円）")
    note = st.text_area("備考", "納期：約2週間\n内容確定後の制作開始となります。")

qty_total = sum(r["qty"] for r in body_rows)
ps, pc = print_unit(qty_total, special)
rows = []
body_total = 0
body_cost = 0
for r in body_rows:
    amount = r["sell"] * r["qty"]
    body_total += amount
    body_cost += r["cost"] * r["qty"]
    rows.append({"item":"ボディ", "desc":r["name"], "qty":f"{r['qty']}枚", "unit":r["sell"], "amount":amount})

print_total = ps * qty_total * print_spots
print_cost = pc * qty_total * print_spots
plate_total = 8000 * plate_count
plate_cost = 5500 * plate_count
if print_spots:
    rows.append({"item":"プリント代", "desc":f"{print_spots}箇所" + (" / 特色" if special else ""), "qty":f"{qty_total}枚", "unit":ps*print_spots, "amount":print_total})
if plate_count:
    rows.append({"item":"製版代", "desc":"シルクスクリーン製版", "qty":f"{plate_count}版", "unit":8000, "amount":plate_total})

subtotal = body_total + print_total + plate_total
tax = subtotal * 0.1
total = subtotal + tax
cost_total = body_cost + print_cost + plate_cost
profit = subtotal - cost_total

with right:
    st.subheader("プレビュー")
    st.markdown(f"### {doc_type}")
    st.markdown(f"**{customer}**  ")
    st.write(f"件名：{subject}")
    st.write(f"番号：{no}")
    st.write(f"発行日：{date.today().strftime('%Y/%m/%d')}")
    st.markdown(f"## {'御見積金額（税込）' if doc_type == '見積書' else '御請求金額（税込）'}")
    st.markdown(f"# {yen(total)}")
    st.table([{ "品目":x["item"], "内容":x["desc"], "数量":x["qty"], "単価":yen(x["unit"]), "金額":yen(x["amount"]) } for x in rows])
    st.write(f"小計：{yen(subtotal)} / 消費税：{yen(tax)} / 合計：{yen(total)}")
    st.info(note)
    st.success(f"管理用：総枚数 {qty_total}枚 / 原価 {yen(cost_total)} / 利益 {yen(profit)}")
    pdf = make_pdf(doc_type, no, customer, subject, rows, subtotal, tax, total, note)
    st.download_button("正式PDFをダウンロード", data=pdf, file_name=f"{no}_{doc_type}.pdf", mime="application/pdf", type="primary")
