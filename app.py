import io
import json
from copy import deepcopy
from datetime import date

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle


st.set_page_config(page_title="HADAOJI PRINT 見積・請求", page_icon="🧾", layout="wide")


DEFAULT_MASTER = {
    "00085-CVT": {
        "name": "5.6oz ヘビーウェイトTシャツ",
        "variants": {
            "100〜150": {"sell": 600, "cost": 400},
            "WM〜XL": {"sell": 660, "cost": 440},
            "XXL〜XXXL": {"sell": 840, "cost": 560},
            "4XL〜5XL": {"sell": 960, "cost": 640},
        },
    },
    "00300-ACT": {
        "name": "4.4oz ドライTシャツ",
        "variants": {
            "100〜150": {"sell": 480, "cost": 320},
            "WM〜LL": {"sell": 516, "cost": 344},
            "3L〜5L": {"sell": 594, "cost": 396},
            "6L〜7L": {"sell": 810, "cost": 540},
        },
    },
    "5001-01": {
        "name": "United Athle 5.6oz Tシャツ",
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
        "name": "United Athle キッズTシャツ",
        "variants": {
            "90〜160 ホワイト": {"sell": 690, "cost": 460},
            "90〜160 カラー": {"sell": 744, "cost": 496},
        },
    },
    "5011-01": {
        "name": "United Athle ロングスリーブTシャツ",
        "variants": {
            "S〜XL ホワイト": {"sell": 1188, "cost": 792},
            "S〜XL カラー": {"sell": 1320, "cost": 880},
            "XXL ホワイト": {"sell": 1392, "cost": 928},
            "XXL カラー": {"sell": 1560, "cost": 1040},
        },
    },
}


def init_state():
    if "master" not in st.session_state:
        st.session_state.master = deepcopy(DEFAULT_MASTER)
    if "body_count" not in st.session_state:
        st.session_state.body_count = 1


def yen(value):
    return f"{int(round(value)):,}円"


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


def paragraph(text, style):
    safe = str(text).replace("\n", "<br/>")
    return Paragraph(safe, style)


def make_pdf(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note, show_bank):
    buffer = io.BytesIO()
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
    )

    base = ParagraphStyle("base", fontName="HeiseiKakuGo-W5", fontSize=9, leading=13)
    small = ParagraphStyle("small", fontName="HeiseiKakuGo-W5", fontSize=8, leading=11)
    title = ParagraphStyle("title", fontName="HeiseiKakuGo-W5", fontSize=22, leading=28, alignment=1)
    brand = ParagraphStyle("brand", fontName="HeiseiKakuGo-W5", fontSize=9, leading=12, alignment=2)

    amount_label = "御見積金額（税込）" if doc_type == "見積書" else "御請求金額（税込）"

    story = []
    story.append(Paragraph(doc_type, title))
    story.append(Spacer(1, 6))

    header = Table(
        [
            [
                paragraph(f"<b>{customer}</b><br/><br/>下記の通りご提出いたします。<br/>件名：{subject}", base),
                paragraph(
                    f"<font size='16'><b>HADAOJI PRINT</b></font><br/>株式会社ハダオジ<br/>"
                    f"見積番号：{quote_no}<br/>発行日：{date.today().strftime('%Y/%m/%d')}",
                    brand,
                ),
            ]
        ],
        colWidths=[100 * mm, 78 * mm],
    )
    header.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (0, 0), 0.8, colors.black),
    ]))
    story.append(header)
    story.append(Spacer(1, 10))

    amount = Table(
        [[Paragraph(f"<b>{amount_label}</b>", base), Paragraph(f"<font size='26'><b>{yen(total)}</b></font>", base)]],
        colWidths=[74 * mm, 104 * mm],
        rowHeights=[19 * mm],
    )
    amount.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2.2, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (-1, -1), colors.Color(0.985, 0.985, 0.985)),
    ]))
    story.append(amount)
    story.append(Spacer(1, 11))

    data = [["項目", "数量", "単価", "金額"]]
    for row in rows:
        item = Paragraph(f"<b>{row['item']}</b><br/><font size='8'>{row['desc']}</font>", small)
        data.append([item, row["qty"], yen(row["unit"]), yen(row["amount"])])

    data += [
        ["", "", "小計", yen(subtotal)],
        ["", "", "消費税10%", yen(tax)],
        ["", "", "合計", yen(total)],
    ]

    table = Table(data, colWidths=[82 * mm, 38 * mm, 29 * mm, 29 * mm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "HeiseiKakuGo-W5"),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.lightgrey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("BACKGROUND", (0, -3), (-1, -1), colors.Color(0.98, 0.98, 0.98)),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    note_table = Table(
        [[Paragraph("<b>備考</b>", base)], [paragraph(note if note else " ", small)]],
        colWidths=[178 * mm],
        rowHeights=[9 * mm, 28 * mm],
    )
    note_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.6, colors.lightgrey),
        ("BACKGROUND", (0, 0), (0, 0), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(note_table)

    if show_bank:
        bank_text = "PayPay銀行<br/>ビジネス営業部（005）<br/>普通 7546092<br/>株式会社ハダオジ<br/>カ）ハダオジ"
        bank_table = Table([[Paragraph("<b>お振込先</b><br/>" + bank_text, small)]], colWidths=[178 * mm])
        bank_table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, colors.lightgrey),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(Spacer(1, 8))
        story.append(bank_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


def add_master_ui():
    with st.expander("ボディマスター登録・確認"):
        tab_add, tab_json = st.tabs(["追加", "JSON確認"])
        with tab_add:
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input("品番", "")
                name = st.text_input("商品名", "")
                variant = st.text_input("区分・サイズ・色", "S〜XL カラー")
            with c2:
                reference_price = st.number_input("参考上代（任意）", 0, 99999, 0)
                auto_calc = st.checkbox("参考上代から自動計算（原価40% / 販売60%）", value=False)
                sell_default = int(reference_price * 0.6) if auto_calc and reference_price else 0
                cost_default = int(reference_price * 0.4) if auto_calc and reference_price else 0
                sell = st.number_input("販売単価", 0, 99999, sell_default)
                cost = st.number_input("原価", 0, 99999, cost_default)
            if st.button("マスターに追加"):
                if code and name and variant:
                    st.session_state.master.setdefault(code, {"name": name, "variants": {}})
                    st.session_state.master[code]["name"] = name
                    st.session_state.master[code]["variants"][variant] = {"sell": sell, "cost": cost}
                    st.success(f"{code} を追加しました")
                else:
                    st.warning("品番・商品名・区分を入力してください")
        with tab_json:
            st.code(json.dumps(st.session_state.master, ensure_ascii=False, indent=2), language="json")


def app():
    init_state()

    st.title("HADAOJI PRINT 見積・請求アプリ v4.2")
    st.caption("正式PDFレイアウト改善 / 複数ボディ / 自由入力 / 簡易マスター登録")

    add_master_ui()

    left, right = st.columns([1, 1.05])

    with left:
        st.subheader("基本情報")
        doc_type = st.selectbox("書類種類", ["見積書", "請求書"])
        quote_no = st.text_input("番号", f"HP-{date.today().strftime('%Y%m%d')}-001")
        customer = st.text_input("宛名", "〇〇 様")
        subject = st.text_input("件名", "オリジナルウェア制作")
        show_bank = st.checkbox("振込先を表示", value=(doc_type == "請求書"))

        st.subheader("ボディ明細")
        c1, c2 = st.columns(2)
        if c1.button("＋ ボディ項目を増やす"):
            st.session_state.body_count += 1
            st.rerun()
        if c2.button("− 1行減らす") and st.session_state.body_count > 1:
            st.session_state.body_count -= 1
            st.rerun()

        body_rows = []
        for idx in range(st.session_state.body_count):
            with st.container(border=True):
                st.markdown(f"**ボディ {idx + 1}**")
                mode = st.selectbox("入力方法", ["マスターから選択", "自由入力"], key=f"mode_{idx}")

                if mode == "マスターから選択":
                    code = st.selectbox("品番", list(st.session_state.master.keys()), key=f"code_{idx}")
                    variant = st.selectbox("区分", list(st.session_state.master[code]["variants"].keys()), key=f"variant_{idx}")
                    item_name = f"{code}\n{st.session_state.master[code]['name']} / {variant}"
                    default_sell = st.session_state.master[code]["variants"][variant]["sell"]
                    default_cost = st.session_state.master[code]["variants"][variant]["cost"]
                    manual = st.checkbox("この行だけ単価を変更", key=f"manual_{idx}")
                    sell = st.number_input("販売単価", 0, 99999, default_sell, key=f"sell_{idx}", disabled=not manual)
                    cost = st.number_input("原価", 0, 99999, default_cost, key=f"cost_{idx}", disabled=not manual)
                else:
                    item_name = st.text_input("品番・商品名・色・サイズ", "未登録ボディ", key=f"free_name_{idx}")
                    sell = st.number_input("販売単価", 0, 99999, 0, key=f"free_sell_{idx}")
                    cost = st.number_input("原価", 0, 99999, 0, key=f"free_cost_{idx}")

                qty = st.number_input("枚数", 1, 9999, 10, key=f"qty_{idx}")
                body_rows.append({"name": item_name, "qty": qty, "sell": sell, "cost": cost})

        st.subheader("プリント")
        print_spots = st.number_input("プリント箇所数", 0, 10, 1)
        plate_count = st.number_input("製版数", 0, 10, 1)
        special = st.checkbox("特色プリント（販売+150円 / 原価+100円）")
        note = st.text_area("備考", "納期：約2週間\n内容確定後の制作開始となります。")

    qty_total = sum(row["qty"] for row in body_rows)
    ps, pc = print_unit(qty_total, special)

    rows = []
    body_total = 0
    body_cost_total = 0
    for body in body_rows:
        amount = body["sell"] * body["qty"]
        body_total += amount
        body_cost_total += body["cost"] * body["qty"]
        rows.append({
            "item": "ボディ",
            "desc": body["name"],
            "qty": f"{body['qty']}枚",
            "unit": body["sell"],
            "amount": amount,
        })

    print_total = ps * qty_total * print_spots
    print_cost_total = pc * qty_total * print_spots
    plate_total = 8000 * plate_count
    plate_cost_total = 5500 * plate_count

    if print_spots:
        rows.append({
            "item": "プリント代",
            "desc": f"{print_spots}箇所" + (" / 特色" if special else ""),
            "qty": f"{qty_total}枚",
            "unit": ps * print_spots,
            "amount": print_total,
        })

    if plate_count:
        rows.append({
            "item": "製版代",
            "desc": "シルクスクリーン製版",
            "qty": f"{plate_count}版",
            "unit": 8000,
            "amount": plate_total,
        })

    subtotal = body_total + print_total + plate_total
    tax = subtotal * 0.1
    total = subtotal + tax
    cost_total = body_cost_total + print_cost_total + plate_cost_total
    profit = subtotal - cost_total
    profit_rate = profit / subtotal * 100 if subtotal else 0

    with right:
        st.subheader("プレビュー")
        st.markdown(f"### {doc_type}")
        st.write(customer)
        st.write(f"件名：{subject}")
        st.write(f"番号：{quote_no}")
        st.markdown(f"## {'御見積金額（税込）' if doc_type == '見積書' else '御請求金額（税込）'}")
        st.markdown(f"# {yen(total)}")
        st.table([
            {
                "項目": row["item"],
                "内容": row["desc"].replace("\n", " / "),
                "数量": row["qty"],
                "単価": yen(row["unit"]),
                "金額": yen(row["amount"]),
            }
            for row in rows
        ])
        st.write(f"小計：{yen(subtotal)} / 消費税：{yen(tax)} / 合計：{yen(total)}")
        st.info(note)
        st.success(f"管理用：総枚数 {qty_total}枚 / 原価 {yen(cost_total)} / 利益 {yen(profit)} / 利益率 {profit_rate:.1f}%")

        pdf = make_pdf(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note, show_bank)
        st.download_button(
            "正式PDFをダウンロード",
            data=pdf,
            file_name=f"{quote_no}_{doc_type}.pdf",
            mime="application/pdf",
            type="primary",
        )


app()
