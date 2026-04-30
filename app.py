from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any

import streamlit as st
from supabase import Client, create_client
import base64
from pathlib import Path


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
HERO_IMAGE_PATH = Path(__file__).parent / "assets" / "hero_gallery_ja.png"


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
                radial-gradient(circle at top left, rgba(255, 226, 186, .34), transparent 30rem),
                linear-gradient(180deg, #fffaf4 0%, #f7f8fb 46%, #ffffff 100%);
        }
        .block-container {
            max-width: 1120px;
            padding-top: 3.2rem;
            padding-bottom: 4rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .brand-label {
            color: #667085;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.45;
            margin-bottom: .4rem;
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
            margin-bottom: .22rem;
        }
        .gallery-sub {
            color: #667085;
            font-size: 1rem;
            line-height: 1.65;
            margin-bottom: 1.25rem;
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
        .thumb-frame {
            align-items: center;
            background: #f4f6f8;
            border: 1px solid #eaecf0;
            border-radius: 10px;
            display: flex;
            height: 280px;
            justify-content: center;
            overflow: hidden;
            width: 100%;
        }
        .thumb-frame img {
            display: block;
            height: 100%;
            max-height: 100%;
            max-width: 100%;
            object-fit: contain;
            width: 100%;
        }
        .card-title {
            color: #182230;
            font-size: 1.22rem;
            font-weight: 830;
            line-height: 1.38;
            margin-top: .9rem;
            margin-bottom: .34rem;
            min-height: 3.35rem;
        }
        .poster-name {
            color: #5d6678;
            font-size: 1rem;
            font-weight: 650;
            line-height: 1.5;
            margin-bottom: .9rem;
        }
        .detail-main {
            max-width: 760px;
            margin: 0 auto;
        }
        .detail-image-note {
            height: .15rem;
        }
        .detail-title {
            color: #182230;
            font-size: 1.85rem;
            font-weight: 860;
            line-height: 1.18;
            margin: 1.25rem 0 .9rem;
        }
        .detail-panel {
            background: rgba(255, 255, 255, .88);
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.05rem;
            margin-top: 1rem;
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
            border-radius: 12px;
            font-size: 1.06rem;
            line-height: 1.72;
            padding: 1rem 1.05rem;
            margin: 1rem 0 1.08rem;
        }
        .focus-label {
            color: #745321;
            font-size: 1rem;
            font-weight: 840;
            line-height: 1.4;
            margin-bottom: .42rem;
        }
        .score-card {
            background: #ffffff;
            border: 1px solid #e1e5eb;
            border-radius: 16px;
            box-shadow: 0 10px 28px rgba(31, 41, 55, .08);
            margin-top: 1.05rem;
            padding: 1.2rem 1rem 1.2rem;
            text-align: center;
        }
        .score-kicker {
            color: #344054;
            font-size: 1rem;
            font-weight: 760;
            line-height: 1.65;
            margin-bottom: .35rem;
        }
        .score-number {
            color: #1f2937;
            font-size: 3.8rem;
            font-weight: 900;
            letter-spacing: 0;
            line-height: 1;
            margin: .25rem 0 .38rem;
        }
        .score-caption {
            color: #667085;
            font-size: 1rem;
            font-weight: 700;
            line-height: 1.4;
        }
        .comments-heading {
            color: #182230;
            font-size: 1.32rem;
            font-weight: 840;
            line-height: 1.4;
            margin: 1.7rem 0 .85rem;
        }
        .ai-comment {
            border-radius: 16px;
            border: 1px solid;
            margin: 0 0 1rem;
            padding: 1rem;
        }
        .ai-comment-jin {
            background: #f0f7ff;
            border-color: #bfdbfe;
        }
        .ai-comment-reina {
            background: #fff1f7;
            border-color: #fbcfe8;
        }
        .ai-comment-takumi {
            background: #effaf3;
            border-color: #bbf7d0;
        }
        .ai-comment-head {
            display: flex;
            align-items: center;
            gap: .72rem;
            margin-bottom: .72rem;
        }
        .ai-avatar {
            align-items: center;
            border-radius: 999px;
            color: #ffffff;
            display: inline-flex;
            flex: 0 0 2.7rem;
            font-size: 1.05rem;
            font-weight: 860;
            height: 2.7rem;
            justify-content: center;
            width: 2.7rem;
        }
        .avatar-jin {
            background: #2563eb;
        }
        .avatar-reina {
            background: #db2777;
        }
        .avatar-takumi {
            background: #16a34a;
        }
        .ai-comment-name {
            color: #1f2937;
            font-size: 1.08rem;
            font-weight: 840;
            line-height: 1.45;
        }
        .ai-comment-body {
            color: #2f3a4a;
            font-size: 1.06rem;
            line-height: 1.78;
        }
        .coming-soon {
            background: #eef7f3;
            border: 1px solid #cee6dc;
            border-radius: 12px;
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
        .soon-text {
            color: #283241;
            font-size: 1.06rem;
            font-weight: 820;
            line-height: 1.55;
        }
        .image-placeholder {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 240px;
            color: #697386;
            background: #f2f4f7;
            border: 1px dashed #cfd5df;
            border-radius: 12px;
            font-size: 1rem;
            line-height: 1.6;
            text-align: center;
            padding: 1rem;
        }
        .thumb-frame .image-placeholder {
            border: 0;
            min-height: 100%;
            width: 100%;
        }
        .stButton > button {
            min-height: 3rem;
            border-radius: 10px;
            font-size: 1.03rem;
            font-weight: 760;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px;
        }
        @media (min-width: 780px) {
            .block-container {
                padding-top: 3.25rem;
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
                font-size: 2.2rem;
            }
            .score-number {
                font-size: 4.4rem;
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
            .detail-main {
                max-width: 100%;
            }
            .detail-title {
                font-size: 1.7rem;
            }
            .thumb-frame {
                height: 280px;
            }
            .card-title {
                min-height: 0;
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


def render_thumbnail(url: str | None) -> None:
    if not url:
        st.markdown(
            '<div class="thumb-frame"><div class="image-placeholder">画像を表示できません</div></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="thumb-frame"><img src="{escape(url, quote=True)}" alt="作品画像"></div>',
        unsafe_allow_html=True,
    )

def render_hero_image() -> None:
    if not HERO_IMAGE_PATH.exists():
        return

    encoded_image = base64.b64encode(HERO_IMAGE_PATH.read_bytes()).decode("ascii")
    st.markdown(
        (
            '<div style="margin: 0.75rem 0 2rem; width: 100%;">'
            f'<img src="data:image/png;base64,{encoded_image}" '
            'alt="その一枚を集めた画廊" '
            'style="width: 100%; height: auto; display: block; border-radius: 14px;">'
            "</div>"
        ),
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
        render_thumbnail(image_url)
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


def render_info_panel(poster_name: str, published_at: str) -> None:
    st.markdown(
        (
            '<div class="detail-panel">'
            '<div class="info-row">'
            '<div class="info-label">投稿者名</div>'
            f'<div class="info-value">{escape(poster_name)}</div>'
            '</div>'
            '<div class="info-row">'
            '<div class="info-label">公開日</div>'
            f'<div class="info-value">{escape(published_at)}</div>'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def render_ai_comment_card(character: str, initial: str, body: str, class_name: str) -> None:
    comment = clean_text(body, "コメントなし")
    st.markdown(
        (
            f'<div class="ai-comment ai-comment-{class_name}">'
            '<div class="ai-comment-head">'
            f'<div class="ai-avatar avatar-{class_name}">{escape(initial)}</div>'
            f'<div class="ai-comment-name">{escape(character)}</div>'
            "</div>"
            f'<div class="ai-comment-body">{escape(comment)}</div>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_detail(work_id: str) -> None:
    client = get_supabase()
    row = fetch_public_work(work_id)

    if row is None:
        st.warning("作品が見つからないか、非公開になりました。")
        if st.button("一覧へ戻る", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        return

    if st.button("← 一覧へ戻る", use_container_width=True):
        st.query_params.clear()
        st.rerun()

    title = clean_text(row.get("share_title"), "Untitled")
    poster_name = clean_text(row.get("poster_name"), "匿名の投稿者")
    published_at = format_date(row.get("created_at"))
    focus_point = clean_text(row.get("focus_point"))
    impression_score = clean_text(row.get("three_vis"), "-")
    image_url = get_image_url(client, row.get("image_path"))

    center_left, center_main, center_right = st.columns([1, 8, 1])
    with center_main:
        st.markdown('<div class="detail-main">', unsafe_allow_html=True)
        render_image(image_url, large=True)
        st.markdown('<div class="detail-image-note"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-title">{escape(title)}</div>', unsafe_allow_html=True)

        render_info_panel(poster_name, published_at)
        render_focus_box(focus_point)
        render_score_card(impression_score)

        st.markdown('<div class="comments-heading">3人コメント</div>', unsafe_allow_html=True)
        render_ai_comment_card("ジンさん", "ジ", clean_text(row.get("comment_jin")), "jin")
        render_ai_comment_card("レイナ", "レ", clean_text(row.get("comment_reina")), "reina")
        render_ai_comment_card("タクミ", "タ", clean_text(row.get("comment_takumi")), "takumi")

        st.markdown(
            (
                '<div class="coming-soon">'
                '<div class="soon-label">Coming soon</div>'
                '<div class="soon-text">この評価をもっと深く見る機能は準備中です</div>'
                "</div>"
            ),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    inject_css()
    render_header()

    work_id = st.query_params.get("work_id")
    if work_id:
        render_detail(str(work_id))
    else:
        render_hero_image()
        render_gallery()


if __name__ == "__main__":
    main()
