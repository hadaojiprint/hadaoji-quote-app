import io
import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import streamlit as st
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import ParagraphStyle


# =========================
# HADAOJI PRINT v8
# =========================

st.set_page_config(
    page_title="HADAOJI PRINT 見積・請求",
    page_icon="🧾",
    layout="wide",
)

APP_DIR = Path(__file__).parent
LOGO_FILE = APP_DIR / "logo.png"
BODY_MASTER_FILE = APP_DIR / "body_master.json"
CUSTOMER_MASTER_FILE = APP_DIR / "customer_master.json"

BRAND_NAME = "HADAOJI PRINT"
COMPANY_NAME = "株式会社ハダオジ"
EMAIL = "hadaojiprint@gmail.com"
CORPORATE_NO = "6050001053912"

BANK_INFO = {
    "bank": "PayPay銀行",
    "branch": "ビジネス営業部（005）",
    "type": "普通",
    "number": "7546092",
    "name": "株式会社ハダオジ（カ）ハダオジ）",
}

DEFAULT_BODY_MASTER = {
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

DEFAULT_CUSTOMER_MASTER = {
    "自由入力": {"name": "", "person": "", "memo": ""},
    "常総学院高等学校ラグビー部": {
        "name": "常総学院高等学校ラグビー部 様",
        "person": "",
        "memo": "部活動・イベントウェア",
    },
    "大翔工業": {
        "name": "大翔工業株式会社 御中",
        "person": "",
        "memo": "設備屋さん・作業着プリント",
    },
    "REI FARM": {
        "name": "REI FARM 御中",
        "person": "",
        "memo": "農業・企業ロゴ",
    },
}


def load_json(path: Path, default: dict) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return deepcopy(default)
    return deepcopy(default)


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def init_state() -> None:
    if "body_master" not in st.session_state:
        st.session_state.body_master = load_json(BODY_MASTER_FILE, DEFAULT_BODY_MASTER)
    if "customer_master" not in st.session_state:
        st.session_state.customer_master = load_json(CUSTOMER_MASTER_FILE, DEFAULT_CUSTOMER_MASTER)
    if "body_count" not in st.session_state:
        st.session_state.body_count = 1


def yen(value: float) -> str:
    return f"{int(round(value)):,}円"


def quote_no_default() -> str:
    return f"HP-{date.today().strftime('%Y%m%d')}-001"


def print_unit(qty: int, special: bool) -> tuple[int, int]:
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


def p(text, style):
    return Paragraph(str(text).replace("\n", "<br/>"), style)


def safe_logo(width=22 * mm, height=22 * mm):
    if not LOGO_FILE.exists():
        return None
    try:
        img = Image(str(LOGO_FILE), width=width, height=height)
        img.hAlign = "LEFT"
        return img
    except Exception:
        return None


# =========================
# PDF v8 layout
# =========================

def make_pdf(
    doc_type: str,
    quote_no: str,
    customer: str,
    subject: str,
    rows: list[dict],
    subtotal: float,
    tax: float,
    total: float,
    note: str,
    show_bank: bool,
):
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
    title = ParagraphStyle("title", fontName="HeiseiKakuGo-W5", fontSize=24, leading=30, alignment=1)
    center = ParagraphStyle("center", fontName="HeiseiKakuGo-W5", fontSize=9, leading=12, alignment=1)
    amount_num = ParagraphStyle("amount_num", fontName="HeiseiKakuGo-W5", fontSize=28, leading=34, alignment=1)
    company_style = ParagraphStyle("company", fontName="HeiseiKakuGo-W5", fontSize=8.8, leading=12, alignment=0)

    dark = HexColor("#3A3A3A")
    light = HexColor("#F5F5F5")
    blue_light = HexColor("#EAF6FB")
    border = HexColor("#222222")
    accent = HexColor("#F0F7FA")

    story = []

    # Title centered
    story.append(Paragraph(doc_type, title))
    story.append(Spacer(1, 5))

    # Customer and subject
    customer_table = Table(
        [
            [p(f"<font size='12'><b>{customer}</b></font>", base)],
            [p(f"<b>件名：</b>{subject}", base)],
        ],
        colWidths=[178 * mm],
        rowHeights=[11 * mm, 10 * mm],
    )
    customer_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, border),
                ("BACKGROUND", (0, 1), (0, 1), blue_light),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(customer_table)
    story.append(Spacer(1, 8))

    # Company block: logo left + company info right
    logo = safe_logo(width=22 * mm, height=22 * mm)
    logo_cell = logo if logo else p("<b>HADAOJI</b>", base)

    company_info = p(
        f"<font size='11'><b>{BRAND_NAME}</b></font><br/>"
        f"{COMPANY_NAME}<br/>"
        f"Mail：{EMAIL}<br/>"
        f"法人番号：{CORPORATE_NO}<br/>"
        f"見積番号：{quote_no}<br/>"
        f"発行日：{date.today().strftime('%Y/%m/%d')}",
        company_style,
    )

    # Place company block on the right side, with logo at left of company information
    company_inner = Table(
        [[logo_cell, company_info]],
        colWidths=[25 * mm, 58 * mm],
        rowHeights=[28 * mm],
    )
    company_inner.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )

    company_outer = Table(
        [["", company_inner]],
        colWidths=[91 * mm, 87 * mm],
    )
    company_outer.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ]
        )
    )
    story.append(company_outer)
    story.append(Spacer(1, 8))

    # Amount card
    amount_label = "御見積金額（税込）" if doc_type == "見積書" else "御請求金額（税込）"
    amount_table = Table(
        [[p(f"<b>{amount_label}</b>", center)], [Paragraph(yen(total), amount_num)]],
        colWidths=[178 * mm],
        rowHeights=[8 * mm, 16 * mm],
    )
    amount_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 2.0, border),
                ("ROUNDEDCORNERS", [10, 10, 10, 10]),
                ("BACKGROUND", (0, 0), (-1, -1), accent),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(amount_table)
    story.append(Spacer(1, 10))

    # Detail
    data = [["項目", "内容", "数量", "単価", "金額"]]
    for row in rows:
        data.append(
            [
                row["item"],
                p(row["desc"], small),
                row["qty"],
                yen(row["unit"]),
                yen(row["amount"]),
            ]
        )
    data += [
        ["", "", "", "小計", yen(subtotal)],
        ["", "", "", "消費税10%", yen(tax)],
        ["", "", "", "合計", yen(total)],
    ]

    detail = Table(data, colWidths=[31 * mm, 65 * mm, 27 * mm, 27 * mm, 28 * mm])
    detail.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "HeiseiKakuGo-W5"),
                ("GRID", (0, 0), (-1, -1), 0.35, HexColor("#D9D9D9")),
                ("BACKGROUND", (0, 0), (-1, 0), dark),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BACKGROUND", (0, -3), (-1, -1), HexColor("#FAFAFA")),
            ]
        )
    )
    story.append(detail)
    story.append(Spacer(1, 9))

    # Note
    note_table = Table(
        [[p("<b>備考</b>", base)], [p(note if note else " ", small)]],
        colWidths=[178 * mm],
        rowHeights=[8 * mm, 22 * mm],
    )
    note_table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.6, HexColor("#CFCFCF")),
                ("BACKGROUND", (0, 0), (0, 0), light),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(note_table)

    if show_bank:
        bank_text = (
            f"{BANK_INFO['bank']}<br/>"
            f"{BANK_INFO['branch']}<br/>"
            f"{BANK_INFO['type']} {BANK_INFO['number']}<br/>"
            f"{BANK_INFO['name']}"
        )
        bank_table = Table([[p("<b>お振込先</b><br/>" + bank_text, small)]], colWidths=[178 * mm])
        bank_table.setStyle(
            TableStyle(
                [
                    ("BOX", (0, 0), (-1, -1), 0.6, HexColor("#CFCFCF")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story += [Spacer(1, 8), bank_table]

    doc.build(story)
    buffer.seek(0)
    return buffer


# =========================
# UI
# =========================

def master_ui():
    with st.expander("マスター管理"):
        tab_body, tab_customer, tab_data = st.tabs(["ボディ追加", "顧客追加", "データ確認"])

        with tab_body:
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input("品番", "")
                name = st.text_input("商品名", "")
                variant = st.text_input("区分・サイズ・色", "S〜XL カラー")
            with c2:
                reference_price = st.number_input("参考上代", 0, 99999, 0)
                auto_calc = st.checkbox("参考上代から自動計算（原価40% / 販売60%）")
                sell_default = int(reference_price * 0.6) if auto_calc and reference_price else 0
                cost_default = int(reference_price * 0.4) if auto_calc and reference_price else 0
                sell = st.number_input("販売単価", 0, 99999, sell_default)
                cost = st.number_input("原価", 0, 99999, cost_default)

            if st.button("ボディマスターに保存"):
                if code and name and variant:
                    st.session_state.body_master.setdefault(code, {"name": name, "variants": {}})
                    st.session_state.body_master[code]["name"] = name
                    st.session_state.body_master[code]["variants"][variant] = {"sell": sell, "cost": cost}
                    save_json(BODY_MASTER_FILE, st.session_state.body_master)
                    st.success("保存しました")
                else:
                    st.warning("品番・商品名・区分を入力してください")

        with tab_customer:
            customer_key = st.text_input("顧客キー", "")
            customer_name = st.text_input("宛名表示", "")
            customer_person = st.text_input("担当者", "")
            customer_memo = st.text_area("メモ", "")
            if st.button("顧客マスターに保存"):
                if customer_key and customer_name:
                    st.session_state.customer_master[customer_key] = {
                        "name": customer_name,
                        "person": customer_person,
                        "memo": customer_memo,
                    }
                    save_json(CUSTOMER_MASTER_FILE, st.session_state.customer_master)
                    st.success("保存しました")
                else:
                    st.warning("顧客キーと宛名表示を入力してください")

        with tab_data:
            st.write("ボディマスター")
            st.code(json.dumps(st.session_state.body_master, ensure_ascii=False, indent=2), language="json")
            st.write("顧客マスター")
            st.code(json.dumps(st.session_state.customer_master, ensure_ascii=False, indent=2), language="json")


def preview_html(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note):
    amount_label = "御見積金額（税込）" if doc_type == "見積書" else "御請求金額（税込）"
    tr = ""
    for r in rows:
        tr += (
            f"<tr><td>{r['item']}</td><td>{r['desc'].replace(chr(10), ' / ')}</td>"
            f"<td>{r['qty']}</td><td>{yen(r['unit'])}</td><td>{yen(r['amount'])}</td></tr>"
        )

    return f"""
    <style>
      .paper {{
        background:#fff;
        border:1px solid #ddd;
        padding:18px;
        box-shadow:0 2px 10px rgba(0,0,0,.08);
        color:#111;
      }}
      .title {{
        text-align:center;
        font-size:26px;
        font-weight:800;
        margin-bottom:12px;
      }}
      .customer {{
        border:1px solid #222;
        margin-top:8px;
      }}
      .customer div {{
        padding:8px 10px;
      }}
      .subject {{
        background:#eaf6fb;
        border-top:1px solid #222;
      }}
      .company-row {{
        display:flex;
        justify-content:flex-end;
        margin:14px 0;
      }}
      .company-box {{
        display:flex;
        gap:10px;
        align-items:flex-start;
        width:330px;
      }}
      .logo-placeholder {{
        width:70px;
        height:70px;
        border:1px solid #ddd;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:11px;
      }}
      .company {{
        text-align:left;
        font-size:12px;
        line-height:1.45;
      }}
      .amount {{
        margin:14px 0;
        border:2px solid #222;
        border-radius:14px;
        background:#f0f7fa;
        text-align:center;
        padding:9px;
      }}
      .amount .label {{
        font-weight:700;
      }}
      .amount .price {{
        font-size:34px;
        font-weight:900;
      }}
      table.preview {{
        width:100%;
        border-collapse:collapse;
        font-size:12px;
      }}
      table.preview th {{
        background:#3a3a3a;
        color:white;
      }}
      table.preview th, table.preview td {{
        border:1px solid #ddd;
        padding:7px;
      }}
      table.preview td:nth-child(3), table.preview td:nth-child(4), table.preview td:nth-child(5) {{
        text-align:right;
      }}
      .note {{
        margin-top:12px;
        border:1px solid #ccc;
      }}
      .note-title {{
        background:#f5f5f5;
        padding:7px;
        font-weight:700;
      }}
      .note-body {{
        padding:8px;
        min-height:45px;
      }}
    </style>
    <div class="paper">
      <div class="title">{doc_type}</div>

      <div class="customer">
        <div><b>{customer}</b></div>
        <div class="subject"><b>件名：</b>{subject}</div>
      </div>

      <div class="company-row">
        <div class="company-box">
          <div class="logo-placeholder">LOGO</div>
          <div class="company">
            <b>{BRAND_NAME}</b><br>
            {COMPANY_NAME}<br>
            Mail：{EMAIL}<br>
            法人番号：{CORPORATE_NO}<br>
            見積番号：{quote_no}<br>
            発行日：{date.today().strftime('%Y/%m/%d')}
          </div>
        </div>
      </div>

      <div class="amount">
        <div class="label">{amount_label}</div>
        <div class="price">{yen(total)}</div>
      </div>

      <table class="preview">
        <tr><th>項目</th><th>内容</th><th>数量</th><th>単価</th><th>金額</th></tr>
        {tr}
        <tr><td colspan="4">小計</td><td>{yen(subtotal)}</td></tr>
        <tr><td colspan="4">消費税10%</td><td>{yen(tax)}</td></tr>
        <tr><td colspan="4"><b>合計</b></td><td><b>{yen(total)}</b></td></tr>
      </table>

      <div class="note">
        <div class="note-title">備考</div>
        <div class="note-body">{note.replace(chr(10), '<br>')}</div>
      </div>
    </div>
    """


def app():
    init_state()

    st.title("HADAOJI PRINT 見積・請求アプリ v8")
    st.caption("フルリニューアル / 会社情報左詰 / ロゴ左 / 金額角丸 / 濃グレー明細")

    master_ui()

    left, right = st.columns([1, 1.05])

    with left:
        st.subheader("基本情報")
        doc_type = st.selectbox("書類種類", ["見積書", "請求書"])
        quote_no = st.text_input("番号", quote_no_default())

        customer_mode = st.radio("宛名入力", ["顧客マスター", "自由入力"], horizontal=True)
        if customer_mode == "顧客マスター":
            customer_key = st.selectbox("顧客", list(st.session_state.customer_master.keys()))
            if customer_key == "自由入力":
                customer = st.text_input("宛名", "〇〇 様")
            else:
                customer = st.session_state.customer_master[customer_key]["name"]
                st.caption(st.session_state.customer_master[customer_key].get("memo", ""))
        else:
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
                    code = st.selectbox("品番", list(st.session_state.body_master.keys()), key=f"code_{idx}")
                    variant = st.selectbox(
                        "区分",
                        list(st.session_state.body_master[code]["variants"].keys()),
                        key=f"variant_{idx}",
                    )
                    item_name = f"{code}\n{st.session_state.body_master[code]['name']} / {variant}"
                    default_sell = st.session_state.body_master[code]["variants"][variant]["sell"]
                    default_cost = st.session_state.body_master[code]["variants"][variant]["cost"]
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
        rows.append(
            {
                "item": "ボディ",
                "desc": body["name"],
                "qty": f"{body['qty']}枚",
                "unit": body["sell"],
                "amount": amount,
            }
        )

    print_total = ps * qty_total * print_spots
    print_cost_total = pc * qty_total * print_spots
    plate_total = 8000 * plate_count
    plate_cost_total = 5500 * plate_count

    if print_spots:
        rows.append(
            {
                "item": "プリント代",
                "desc": f"{print_spots}箇所" + (" / 特色" if special else ""),
                "qty": f"{qty_total}枚",
                "unit": ps * print_spots,
                "amount": print_total,
            }
        )

    if plate_count:
        rows.append(
            {
                "item": "製版代",
                "desc": "シルクスクリーン製版",
                "qty": f"{plate_count}版",
                "unit": 8000,
                "amount": plate_total,
            }
        )

    subtotal = body_total + print_total + plate_total
    tax = subtotal * 0.1
    total = subtotal + tax
    cost_total = body_cost_total + print_cost_total + plate_cost_total
    profit = subtotal - cost_total
    profit_rate = profit / subtotal * 100 if subtotal else 0

    with right:
        st.subheader("プレビュー")
        st.markdown(
            preview_html(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note),
            unsafe_allow_html=True,
        )
        st.success(
            f"管理用：総枚数 {qty_total}枚 / 原価 {yen(cost_total)} / 利益 {yen(profit)} / 利益率 {profit_rate:.1f}%"
        )

        pdf = make_pdf(doc_type, quote_no, customer, subject, rows, subtotal, tax, total, note, show_bank)
        st.download_button(
            "正式PDFをダウンロード",
            data=pdf,
            file_name=f"{quote_no}_{doc_type}.pdf",
            mime="application/pdf",
            type="primary",
        )


app()