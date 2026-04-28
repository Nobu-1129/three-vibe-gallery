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
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 222, 173, .3), transparent 34rem),
                linear-gradient(180deg, #fffaf3 0%, #f6f8fb 46%, #ffffff 100%);
        }
        .block-container {
            max-width: 1180px;
            padding-top: 2.1rem;
            padding-bottom: 4rem;
        }
        .brand-label {
            color: #667085;
            font-size: .92rem;
            font-weight: 700;
            margin-bottom: .32rem;
        }
        .gallery-title {
            color: #1f2937;
            font-size: 2.45rem;
            font-weight: 850;
            line-height: 1.08;
            margin-bottom: .42rem;
        }
        .gallery-title span {
            color: #4b5563;
            font-size: 1.34rem;
            font-weight: 760;
        }
        .gallery-lead {
            color: #202938;
            font-size: 1.12rem;
            font-weight: 650;
            margin-bottom: .25rem;
        }
        .gallery-sub {
            color: #667085;
            margin-bottom: 1.65rem;
        }
        .section-label {
            color: #344054;
            font-size: 1rem;
            font-weight: 800;
            margin: .9rem 0 .65rem;
        }
        .card-image-wrap img {
            border-radius: 7px;
        }
        .card-title {
            color: #182230;
            font-size: 1.08rem;
            font-weight: 820;
            line-height: 1.34;
            margin-top: .72rem;
            margin-bottom: .25rem;
        }
        .meta {
            color: #667085;
            font-size: .85rem;
            line-height: 1.48;
            margin-bottom: .55rem;
        }
        .score-badge {
            display: inline-flex;
            width: fit-content;
            color: #322100;
            background: #ffe7ad;
            border: 1px solid #f1c96d;
            border-radius: 999px;
            font-size: .9rem;
            font-weight: 840;
            padding: .24rem .64rem;
            margin: .1rem 0 .68rem;
        }
        .focus-box {
            color: #303948;
            background: #fbf7ef;
            border: 1px solid #eadfcd;
            border-left: 4px solid #d29b4a;
            border-radius: 8px;
            font-size: .92rem;
            line-height: 1.6;
            padding: .72rem .78rem;
            margin: .18rem 0 .88rem;
        }
        .focus-label {
            color: #745321;
            font-size: .78rem;
            font-weight: 840;
            margin-bottom: .24rem;
        }
        .detail-panel {
            background: rgba(255, 255, 255, .82);
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 1rem 1.05rem;
        }
        .detail-title {
            color: #182230;
            font-size: 2rem;
            font-weight: 860;
            line-height: 1.16;
            margin-bottom: .75rem;
        }
        .info-row {
            border-bottom: 1px solid #edf0f4;
            padding: .58rem 0;
        }
        .info-row:last-child {
            border-bottom: 0;
        }
        .info-label {
            color: #697386;
            font-size: .82rem;
            font-weight: 760;
            margin-bottom: .12rem;
        }
        .info-value {
            color: #1f2937;
            font-size: .98rem;
            font-weight: 650;
        }
        .comment-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            min-height: 150px;
            padding: .95rem;
        }
        .comment-name {
            color: #283241;
            font-weight: 830;
            margin-bottom: .45rem;
        }
        .comment-body {
            color: #3b4656;
            font-size: .95rem;
            line-height: 1.68;
        }
        .coming-soon {
            background: #eef7f3;
            border: 1px solid #cee6dc;
            border-radius: 8px;
            margin-top: 1.2rem;
            padding: 1rem 1.1rem;
        }
        .soon-label {
            display: inline-block;
            color: #116149;
            background: #d9f0e8;
            border-radius: 999px;
            font-size: .76rem;
            font-weight: 840;
            padding: .16rem .55rem;
            margin-bottom: .42rem;
        }
        .image-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 220px;
            color: #697386;
            background: #f2f4f7;
            border: 1px dashed #cfd5df;
            border-radius: 8px;
            text-align: center;
            padding: 1rem;
        }
        @media (max-width: 760px) {
            .gallery-title {
                font-size: 2rem;
            }
            .gallery-title span {
                font-size: 1.18rem;
            }
            .detail-title {
                font-size: 1.55rem;
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
        height = 360 if large else 220
        st.markdown(
            f'<div class="image-placeholder" style="min-height: {height}px;">画像を表示できません</div>',
            unsafe_allow_html=True,
        )
        return

    try:
        st.markdown('<div class="card-image-wrap">', unsafe_allow_html=True)
        st.image(url, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception:
        height = 360 if large else 220
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


def render_card(client: Client, row: dict[str, Any]) -> None:
    work_id = clean_text(row.get("id"))
    title = clean_text(row.get("share_title"), "Untitled")
    poster_name = clean_text(row.get("poster_name"), "匿名の投稿者")
    published_at = format_date(row.get("created_at"))
    three_vis = clean_text(row.get("three_vis"), "-")
    focus_point = clean_text(row.get("focus_point"))
    image_url = get_image_url(client, row.get("image_path"))

    with st.container(border=True):
        render_image(image_url)
        st.markdown(f'<div class="card-title">{escape(title)}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="meta">by {escape(poster_name)}<br>公開日 {escape(published_at)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="score-badge">3VIS: {escape(three_vis)}</div>', unsafe_allow_html=True)
        render_focus_box(focus_point)

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
    three_vis = clean_text(row.get("three_vis"), "-")
    focus_point = clean_text(row.get("focus_point"))
    image_url = get_image_url(client, row.get("image_path"))

    left, right = st.columns([1.28, 1], gap="large")
    with left:
        render_image(image_url, large=True)

    with right:
        st.markdown('<div class="detail-panel">', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-title">{escape(title)}</div>', unsafe_allow_html=True)
        render_info_row("投稿者名", poster_name)
        render_info_row("公開日", published_at)
        render_info_row("3VIS", three_vis)
        if focus_point:
            st.markdown('<div class="info-row"><div class="info-label">ココ見てほしい</div>', unsafe_allow_html=True)
            render_focus_box(focus_point)
            st.markdown("</div>", unsafe_allow_html=True)
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
