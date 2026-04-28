from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import streamlit as st
from supabase import Client, create_client


GALLERY_NAME = "Three Vibe Gallery"
GALLERY_NAME_JA = "そのイチギャラリー"
EVALUATION_APP_NAME = "Three Vibe Impression"
EVALUATION_APP_NAME_JA = "そのイチ印象値"
TAGLINE = "その一枚、私達にも見せてもらえませんか？"

TABLE_NAME = "image_evaluations"
BUCKET_NAME = "evaluation-images"
PAGE_SIZE = 24
SELECT_COLUMNS = (
    "id,created_at,share_title,poster_name,focus_point,three_vis,"
    "comment_jin,comment_reina,comment_takumi,image_path,is_public"
)


st.set_page_config(
    page_title=f"{GALLERY_NAME} | {GALLERY_NAME_JA}",
    page_icon=":art:",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        html {
            font-size: 16px;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 226, 186, .36), transparent 30rem),
                linear-gradient(180deg, #fffaf4 0%, #f7f8fb 46%, #ffffff 100%);
        }
        .block-container {
            max-width: 1160px;
            padding-top: 3rem;
            padding-bottom: 4rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .brand-label {
            color: #667085;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.45;
            margin-bottom: .45rem;
        }
        .gallery-title {
            color: #1f2937;
            font-size: 2.05rem;
            font-weight: 850;
            line-height: 1.12;
            margin-bottom: .55rem;
        }
        .gallery-title span {
            color: #4b5563;
            display: inline-block;
            font-size: 1.35rem;
            font-weight: 760;
            margin-top: .18rem;
        }
        .gallery-lead {
            color: #202938;
            font-size: 1.13rem;
            font-weight: 680;
            line-height: 1.6;
            margin-bottom: .25rem;
        }
        .gallery-sub {
            color: #667085;
            font-size: 1rem;
            line-height: 1.65;
            margin-bottom: 1.7rem;
        }
        .section-label {
            color: #344054;
            font-size: 1.12rem;
            font-weight: 820;
            margin: 1rem 0 .8rem;
        }
        .gallery-card {
            padding: .25rem 0 .45rem;
        }
        .gallery-card img {
            border-radius: 8px;
        }
        .card-title {
            color: #182230;
            font-size: 1.22rem;
            font-weight: 830;
            line-height: 1.38;
            margin-top: .9rem;
            margin-bottom: .34rem;
        }
        .poster-name {
            color: #5d6678;
            font-size: 1rem;
            font-weight: 650;
            line-height: 1.5;
            margin-bottom: .9rem;
        }
        .detail-title {
            color: #182230;
            font-size: 1.85rem;
            font-weight: 860;
            line-height: 1.18;
            margin: 1.15rem 0 .85rem;
        }
        .detail-panel {
            background: rgba(255, 255, 255, .86);
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.05rem;
        }
        .info-row {
            border-bottom: 1px solid #edf0f4;
            padding: .72rem 0;
        }
        .info-row:last-child {
            border-bottom: 0;
        }
        .info-label {
            color: #697386;
            font-size: 1rem;
            font-weight: 760;
            line-height: 1.45;
            margin-bottom: .18rem;
        }
        .info-value {
            color: #1f2937;
            font-size: 1.06rem;
            font-weight: 650;
            line-height: 1.55;
        }
        .focus-box {
            color: #303948;
            background: #fbf7ef;
            border: 1px solid #eadfcd;
            border-left: 5px solid #d29b4a;
            border-radius: 10px;
            font-size: 1.05rem;
            line-height: 1.7;
            padding: .95rem 1rem;
            margin: .95rem 0 1.05rem;
        }
        .focus-label {
            color: #745321;
            font-size: 1rem;
            font-weight: 840;
            line-height: 1.4;
            margin-bottom: .4rem;
        }
        .score-card {
            background: #ffffff;
            border: 1px solid #e1e5eb;
            border-radius: 14px;
            box-shadow: 0 10px 28px rgba(31, 41, 55, .08);
            margin-top: 1rem;
            padding: 1.1rem 1rem 1.15rem;
            text-align: center;
        }
        .score-kicker {
            color: #344054;
            font-size: 1rem;
            font-weight: 760;
            line-height: 1.6;
            margin-bottom: .35rem;
        }
        .score-number {
            color: #1f2937;
            font-size: 3.6rem;
            font-weight: 900;
            letter-spacing: 0;
            line-height: 1;
            margin: .2rem 0 .35rem;
        }
        .score-caption {
            color: #667085;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
        }
        .comment-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            min-height: 150px;
            padding: 1rem;
        }
        .comment-name {
            color: #283241;
            font-size: 1.06rem;
            font-weight: 830;
            line-height: 1.45;
            margin-bottom: .55rem;
        }
        .comment-body {
            color: #3b4656;
            font-size: 1.03rem;
            line-height: 1.72;
        }
        .coming-soon {
            background: #eef7f3;
            border: 1px solid #cee6dc;
            border-radius: 10px;
            margin-top: 1.25rem;
            padding: 1.1rem;
        }
        .soon-label {
            display: inline-block;
            color: #116149;
            background: #d9f0e8;
            border-radius: 999px;
            font-size: .95rem;
            font-weight: 840;
            line-height: 1.35;
            padding: .22rem .68rem;
            margin-bottom: .55rem;
        }
        .image-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 240px;
            color: #697386;
            background: #f2f4f7;
            border: 1px dashed #cfd5df;
            border-radius: 10px;
            font-size: 1rem;
            line-height: 1.6;
            text-align: center;
            padding: 1rem;
        }
        .stButton > button {
            min-height: 3rem;
            border-radius: 10px;
            font-size: 1.03rem;
            font-weight: 760;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
        }
        @media (min-width: 780px) {
            .block-container {
                padding-top: 3.2rem;
                padding-left: 2rem;
                padding-right: 2rem;
            }
            .gallery-title {
                font-size: 2.65rem;
            }
            .gallery-title span {
                font-size: 1.45rem;
            }
            .detail-title {
                margin-top: 0;
                font-size: 2.15rem;
            }
            .score-number {
                font-size: 4.2rem;
            }
        }
        @media (max-width: 760px) {
            .block-container {
                padding-top: 3.4rem;
            }
            div[data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
            }
            div[data-testid="stHorizontalBlock"] {
                gap: 1.05rem;
            }
            .gallery-title {
                font-size: 2rem;
            }
            .detail-panel {
                margin-top: .3rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_ANON_KEY"])


def clean_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def format_date(value: Any) -> str:
    raw = clean_text(value)
    if not raw:
        return "日付未設定"

    normalized = raw.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%Y.%m.%d")
    except ValueError:
        return raw[:10] if len(raw) >= 10 else raw


def get_image_url(client: Client, image_path: Any) -> str | None:
    path = clean_text(image_path)
    if not path:
        return None

    try:
        if path.lower().startswith(("http://", "https://")):
            return path

        storage_path = path.lstrip("/")
        bucket_prefix = f"{BUCKET_NAME}/"
        if storage_path.startswith(bucket_prefix):
            storage_path = storage_path[len(bucket_prefix) :]

        public_url = client.storage.from_(BUCKET_NAME).get_public_url(storage_path)
        return str(public_url) if public_url else None
    except Exception:
        return None


def render_image(url: str | None, *, large: bool = False) -> None:
    if not url:
        height = 380 if large else 260
        st.markdown(
            f'<div class="image-placeholder" style="min-height: {height}px;">画像を表示できません</div>',
            unsafe_allow_html=True,
        )
        return

    try:
        st.image(url, use_container_width=True)
    except Exception:
        height = 380 if large else 260
        st.markdown(
            f'<div class="image-placeholder" style="min-height: {height}px;">画像を表示できません</div>',
            unsafe_allow_html=True,
        )


@st.cache_data(ttl=60)
def fetch_public_works(limit: int = PAGE_SIZE) -> list[dict[str, Any]]:
    client = get_supabase()
    response = (
        client.table(TABLE_NAME)
        .select(SELECT_COLUMNS)
        .eq("is_public", True)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return response.data or []


@st.cache_data(ttl=60)
def fetch_public_work(work_id: str) -> dict[str, Any] | None:
    client = get_supabase()
    response = (
        client.table(TABLE_NAME)
        .select(SELECT_COLUMNS)
        .eq("is_public", True)
        .eq("id", work_id)
        .limit(1)
        .execute()
    )
    rows = response.data or []
    return rows[0] if rows else None


def render_header() -> None:
    st.markdown(
        f'<div class="brand-label">{EVALUATION_APP_NAME} / {EVALUATION_APP_NAME_JA} 公開作品ギャラリー</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="gallery-title">{GALLERY_NAME}<br><span>{GALLERY_NAME_JA}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(f'<div class="gallery-lead">{TAGLINE}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="gallery-sub">公開された作品だけを集めた、見るだけで楽しい小さな画廊です。</div>',
        unsafe_allow_html=True,
    )


def render_focus_box(text: str) -> None:
    if not text:
        return

    st.markdown(
        (
            '<div class="focus-box">'
            '<div class="focus-label">ココ見てほしい</div>'
            f"{escape(text)}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_score_card(score: str) -> None:
    st.markdown(
        (
            '<div class="score-card">'
            '<div class="score-kicker">この画像に3人のAIキャラが勝手につけた印象値</div>'
            f'<div class="score-number">{escape(score)}</div>'
            '<div class="score-caption">Your Three Vibe Impression Score</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_card(client: Client, row: dict[str, Any]) -> None:
    work_id = clean_text(row.get("id"))
    title = clean_text(row.get("share_title"), "Untitled")
    poster_name = clean_text(row.get("poster_name"), "匿名の投稿者")
    image_url = get_image_url(client, row.get("image_path"))

    with st.container(border=True):
        st.markdown('<div class="gallery-card">', unsafe_allow_html=True)
        render_image(image_url)
        st.markdown(f'<div class="card-title">{escape(title)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="poster-name">by {escape(poster_name)}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("詳細を見る", key=f"detail-{work_id}", use_container_width=True):
            st.query_params["work_id"] = work_id
            st.rerun()


def render_gallery() -> None:
    client = get_supabase()
    works = fetch_public_works()

    if not works:
        st.info("公開中の作品はまだありません。")
        return

    st.markdown('<div class="section-label">新着作品</div>', unsafe_allow_html=True)
    columns = st.columns(3, gap="large")
    for index, row in enumerate(works):
        with columns[index % 3]:
            render_card(client, row)


def render_info_row(label: str, body: str) -> None:
    st.markdown(
        (
            '<div class="info-row">'
            f'<div class="info-label">{escape(label)}</div>'
            f'<div class="info-value">{escape(body)}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_comment_card(name: str, body: str) -> None:
    comment = clean_text(body, "コメントなし")
    st.markdown(
        (
            '<div class="comment-card">'
            f'<div class="comment-name">{escape(name)}</div>'
            f'<div class="comment-body">{escape(comment)}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_detail(work_id: str) -> None:
    client = get_supabase()
    row = fetch_public_work(work_id)

    if row is None:
        st.warning("作品が見つからないか、非公開になりました。")
        if st.button("一覧へ戻る"):
            st.query_params.clear()
            st.rerun()
        return

    if st.button("← 一覧へ戻る"):
        st.query_params.clear()
        st.rerun()

    title = clean_text(row.get("share_title"), "Untitled")
    poster_name = clean_text(row.get("poster_name"), "匿名の投稿者")
    published_at = format_date(row.get("created_at"))
    focus_point = clean_text(row.get("focus_point"))
    impression_score = clean_text(row.get("three_vis"), "-")
    image_url = get_image_url(client, row.get("image_path"))

    left, right = st.columns([1.28, 1], gap="large")
    with left:
        render_image(image_url, large=True)

    with right:
        st.markdown('<div class="detail-panel">', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-title">{escape(title)}</div>', unsafe_allow_html=True)
        render_info_row("投稿者名", poster_name)
        render_info_row("公開日", published_at)
        render_focus_box(focus_point)
        render_score_card(impression_score)
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 3人コメント")
    comment_columns = st.columns(3, gap="large")
    comments = [
        ("ジンさんのコメント", clean_text(row.get("comment_jin"))),
        ("レイナのコメント", clean_text(row.get("comment_reina"))),
        ("タクミのコメント", clean_text(row.get("comment_takumi"))),
    ]
    for index, (name, comment) in enumerate(comments):
        with comment_columns[index]:
            render_comment_card(name, comment)

    st.markdown(
        (
            '<div class="coming-soon">'
            '<div class="soon-label">Coming soon</div>'
            '<div class="comment-name">この評価をもっと深く見る機能は準備中です</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def main() -> None:
    inject_css()
    render_header()

    work_id = st.query_params.get("work_id")
    if work_id:
        render_detail(str(work_id))
    else:
        render_gallery()


if __name__ == "__main__":
    main()
