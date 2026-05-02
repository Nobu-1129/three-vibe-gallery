from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any
from urllib.parse import quote
import json

import streamlit as st
import streamlit.components.v1 as components
from supabase import Client, create_client
import base64
import os
from pathlib import Path


GALLERY_NAME = "Three Vibe Gallery"
GALLERY_NAME_JA = "そのイチギャラリー"
EVALUATION_APP_NAME = "Three Vibe Impression"
EVALUATION_APP_NAME_JA = "そのイチ印象値"
TAGLINE = "その一枚、私達にも見せてもらえませんか？"

IMPRESSION_APP_URL = "https://three-vibe-impression-app-amy8zqpimaqbtkf4grxqj6.streamlit.app"
TABLE_NAME = "image_evaluations"
BUCKET_NAME = "evaluation-images"
PAGE_SIZE = 24
SELECT_COLUMNS = (
    "id,created_at,share_title,poster_name,poster_profile,focus_point,three_vis,"
    "appeal_targets,"
    "comment_jin,comment_reina,comment_takumi,image_path,is_public"
)
HERO_IMAGE_PATH = Path(__file__).parent / "assets" / "hero_gallery_ja_mobile.jpg"


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

        .works-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1.2rem;
        }

        .work-card {
            background: rgba(255, 255, 255, .9);
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: .9rem;
            box-sizing: border-box;
        }
        
        .work-thumb {
            height: 220px;
            background: #f4f6f8;
            border: 1px solid #eaecf0;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        .work-thumb img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
        }
        
        .work-title {
            color: #182230;
            font-size: 1.05rem;
            font-weight: 830;
            line-height: 1.35;
            margin-top: .75rem;
            min-height: 2.8rem;
        }

        .work-poster {
            color: #5d6678;
            font-size: .9rem;
            font-weight: 650;
            margin-top: .35rem;
        }

        .tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: .28rem;
            margin-top: .45rem;
            min-height: 1.6rem;
        }

        .tag-chip {
            display: inline-flex;
            align-items: center;
            background: #f2f4f7;
            border: 1px solid #e5e7eb;
            border-radius: 999px;
            color: #475467;
            font-size: .78rem;
            font-weight: 700;
            line-height: 1.2;
            padding: .22rem .5rem;
            white-space: nowrap;
        }

        .tag-filter-wrap {
            display: flex;
            flex-wrap: nowrap;
            gap: .45rem;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            padding: .25rem 0 .65rem;
            margin: .2rem 0 .7rem;
        }

        .tag-filter-wrap::-webkit-scrollbar {
            height: 6px;
        }

        .tag-filter-wrap::-webkit-scrollbar-thumb {
            background: #d0d5dd;
            border-radius: 999px;
        }

        .tag-filter-chip {
            display: inline-flex;
            align-items: center;
            flex: 0 0 auto;
            background: rgba(255, 255, 255, .92);
            border: 1px solid #d0d5dd;
            border-radius: 999px;
            color: #344054;
            font-size: .88rem;
            font-weight: 760;
            line-height: 1.2;
            padding: .42rem .72rem;
            text-decoration: none;
            white-space: nowrap;
        }

        .tag-filter-chip:hover {
            background: #f2f4f7;
        }

        .tag-filter-chip-selected {
            background: #344054;
            border-color: #344054;
            color: #ffffff;
        }

        .tag-filter-chip-selected:hover {
            background: #344054;
            color: #ffffff;
        }

        .tag-filter-box {
            background: rgba(255, 255, 255, .78);
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: .8rem .85rem .55rem;
            margin: .45rem 0 1rem;
        }
        
        .work-button {
            display: block;
            text-align: center;
            margin-top: .75rem;
            padding: .55rem .5rem;
            border: 1px solid #cfd5df;
            border-radius: 9px;
            color: #182230;
            text-decoration: none;
            font-size: .9rem;
            font-weight: 700;
            background: #ffffff;
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

            .works-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: .65rem;
            }

            .work-card {
                padding: .55rem;
            }

            .work-thumb {
                height: 120px;
            }

            .work-title {
                font-size: .75rem;
                line-height: 1.35;
                min-height: 2.1rem;
                margin-top: .45rem;
            }
            
            .work-poster {
                font-size: .68rem;
                margin-top: .2rem;
            }

            .tag-row {
                gap: .2rem;
                margin-top: .3rem;
                min-height: 1.25rem;
            }

            .tag-chip {
                font-size: .58rem;
                padding: .16rem .34rem;
            }

            .tag-filter-wrap {
                gap: .35rem;
                padding-bottom: .55rem;
                margin-bottom: .55rem;
            }

            .tag-filter-chip {
                font-size: .75rem;
                padding: .34rem .56rem;
            }

            .tag-filter-box {
                padding: .65rem .65rem .45rem;
                margin: .35rem 0 .85rem;
            }

            .work-button {
                font-size: .7rem;
                padding: .38rem .3rem;
                margin-top: .45rem;
                border-radius: 7px;
            }
        
            div[data-testid="stHorizontalBlock"] {
                gap: 0.5rem !important;
                flex-wrap: wrap !important;
                align-items: stretch !important;
            }
            
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                width: calc(50% - 0.25rem) !important;
                flex: 0 0 calc(50% - 0.25rem) !important;
                min-width: 0 !important;
            }
        
            .brand-label {
                font-size: 0.85rem;
                line-height: 1.4;
                margin-bottom: 0.6rem;
            }
        
            .gallery-title {
                font-size: 2rem;
            }
        
            .detail-main {
                max-width: 100%;
            }
        
            .detail-title {
                font-size: 1.35rem;
                line-height: 1.35;
                word-break: keep-all;
                overflow-wrap: anywhere;
            }
        
            .thumb-frame {
                height: 135px;
            }
        
            .card-title {
                font-size: 0.78rem;
                line-height: 1.35;
                min-height: 2.2rem;
                margin-top: 0.5rem;
                margin-bottom: 0.2rem;
            }

            .poster-name {
                font-size: 0.75rem;
                margin-bottom: 0.45rem;
            }

            .stButton > button {
                min-height: 2rem;
                font-size: 0.75rem;
                padding: 0.25rem 0.4rem;
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

def normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]

    if isinstance(value, tuple):
        return [clean_text(item) for item in value if clean_text(item)]

    text = clean_text(value)
    if not text:
        return []

    # JSON文字列っぽい場合: ["写真好き","動物好き"]
    if text.startswith("[") and text.endswith("]"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [clean_text(item) for item in parsed if clean_text(item)]
        except Exception:
            pass

    # Postgres配列文字列っぽい場合: {写真好き,動物好き}
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1]
        return [clean_text(item.strip().strip('"')) for item in inner.split(",") if clean_text(item.strip().strip('"'))]

    # 念のためカンマ区切りにも対応
    return [clean_text(item) for item in text.split(",") if clean_text(item)]


def format_tag_label(tag: str) -> str:
    text = clean_text(tag)

    if text.endswith("好き"):
        return text[:-2]

    return text


def make_tag_chips_html(tags: list[str], max_tags: int = 4) -> str:
    safe_tags = tags[:max_tags]

    if not safe_tags:
        return ""

    chips = "".join(
        f'<span class="tag-chip">{escape(format_tag_label(tag))}</span>'
        for tag in safe_tags
    )

    return f'<div class="tag-row">{chips}</div>'

def collect_all_tags(rows: list[dict[str, Any]]) -> list[str]:
    tag_set = set()

    for row in rows:
        tags = normalize_tags(row.get("appeal_targets"))
        for tag in tags:
            if tag:
                tag_set.add(tag)

    return sorted(tag_set)

def make_tag_filter_html(all_tags: list[str], selected_tag: str = "") -> str:
    chips = []

    all_class = "tag-filter-chip tag-filter-chip-selected" if not selected_tag else "tag-filter-chip"
    chips.append(
        f'<a class="{all_class}" href="?" target="_self">すべて</a>'
    )

    for tag in all_tags:
        label = format_tag_label(tag)
        tag_url = f"?tag={quote(tag)}"
        class_name = "tag-filter-chip"

        if tag == selected_tag:
            class_name += " tag-filter-chip-selected"

        chips.append(
            f'<a class="{class_name}" href="{tag_url}" target="_self">{escape(label)}</a>'
        )

    return f'<div class="tag-filter-wrap">{"".join(chips)}</div>'


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
            '<div style="margin: 0.25rem 0 2rem; width: 100%;">'
            f'<img src="data:image/jpeg;base64,{encoded_image}" '
            'alt="その一枚を集めた画廊" '
            'style="width: 100%; height: auto; display: block; border-radius: 14px;">'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

def render_impression_app_link() -> None:
    IMPRESSION_APP_URL = "https://three-vibe-impression-app-amy8zqpimaqbtkf4grxqj6.streamlit.app/"

    st.markdown(
        f"""
<div style="
    margin-top: 28px;
    margin-bottom: 10px;
    text-align: center;
    font-size: 14px;
    line-height: 1.6;
">
  <a href="{IMPRESSION_APP_URL}" target="_blank" style="
      color: #4b5563;
      text-decoration: underline;
      text-underline-offset: 3px;
  ">
    自分の一枚をAI評価してみる
  </a>
</div>
""",
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
        '<div class="brand-label">「その一枚、私達にも見せてもらえませんか？」公開作品ギャラリー</div>',
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
            '<div class="score-kicker">この画像に3人のAIキャラがつけた印象値</div>'
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

    all_tags = collect_all_tags(works)

    selected_tag = st.query_params.get("tag", "")

    if selected_tag and selected_tag not in all_tags:
        selected_tag = ""

    if all_tags:
    if all_tags:
        st.markdown('<div class="section-label">タグで見る</div>', unsafe_allow_html=True)

        tag_display_mode = st.radio(
            "タグ表示方法",
            ["横スクロール", "折りたたみ"],
            horizontal=True,
            label_visibility="collapsed",
        )

        tag_filter_html = make_tag_filter_html(all_tags, selected_tag)

        if tag_display_mode == "折りたたみ":
            with st.expander("タグで絞り込む", expanded=bool(selected_tag)):
                st.markdown(tag_filter_html, unsafe_allow_html=True)
        else:
            st.markdown(tag_filter_html, unsafe_allow_html=True)

        if selected_tag:
            selected_label = format_tag_label(selected_tag)

            st.markdown(
                f"""
                <div style="
                    margin: .35rem 0 1rem;
                    padding: .7rem .85rem;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    background: rgba(255,255,255,.82);
                    color: #344054;
                    font-size: .95rem;
                    font-weight: 700;
                    line-height: 1.5;
                ">
                    「{escape(selected_label)}」の作品を表示中
                </div>
                """,
                unsafe_allow_html=True,
            )

    if selected_tag:
        works = [
            row for row in works
            if selected_tag in normalize_tags(row.get("appeal_targets"))
        ]

    if selected_tag and not works:
        st.info("このタグの公開作品はまだありません。")
        return

    section_title = "絞り込み結果" if selected_tag else "新着作品"
    st.markdown(f'<div class="section-label">{section_title}</div>', unsafe_allow_html=True)

    cards_html = ""

    for row in works:
        work_id = clean_text(row.get("id"))
        title = clean_text(row.get("share_title"), "Untitled")
        poster_name = clean_text(row.get("poster_name"), "匿名の投稿者")
        image_url = get_image_url(client, row.get("image_path"))
        tags = normalize_tags(row.get("appeal_targets"))
        tags_html = make_tag_chips_html(tags)

        if image_url:
            image_html = f'<img src="{escape(image_url)}" alt="{escape(title)}">'
        else:
            image_html = '<div class="image-placeholder">画像なし</div>'

        cards_html += (
            '<article class="work-card">'
            '<div class="work-thumb">'
            f'{image_html}'
            '</div>'
            f'<div class="work-title">{escape(title)}</div>'
            f'<div class="work-poster">by {escape(poster_name)}</div>'
            f'{tags_html}'
            f'<a class="work-button" href="?work_id={escape(work_id)}" target="_self">詳細を見る</a>'
            '</article>'
        )

    gallery_html = (
        '<div class="works-grid">'
        f'{cards_html}'
        '</div>'
    )

    st.markdown(gallery_html, unsafe_allow_html=True)

def render_info_panel(poster_name: str, published_at: str, poster_profile: str = "") -> None:
    profile_html = ""

    if poster_profile:
        profile_html = (
            '<div class="info-row">'
            '<div class="info-label">投稿者プロフィール</div>'
            f'<div class="info-value" style="white-space: pre-wrap;">{escape(poster_profile)}</div>'
            '</div>'
        )

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
            f'{profile_html}'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

CHARACTER_ICON_PATHS = {
    "jin": "assets/icon_jin.jpg",
    "reina": "assets/icon_reina.jpg",
    "takumi": "assets/icon_takumi.jpg",
}

def image_file_to_data_uri(path: str) -> str:
    file_path = Path(__file__).parent / path
    if not file_path.exists():
        return ""

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    ext = file_path.suffix.lower()
    mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

    return f"data:{mime};base64,{encoded}"

def render_ai_comment_card(character: str, initial: str, body: str, class_name: str) -> None:
    comment = clean_text(body, "コメントなし")
    icon_data_uri = image_file_to_data_uri(CHARACTER_ICON_PATHS.get(class_name, ""))

    comment_styles = {
        "jin": {
            "icon_bg": "#cfe0ff",
            "bubble_border": "#9bbcf7",
            "bubble_bg": "#f3f8ff",
            "reverse": False,
        },
        "reina": {
            "icon_bg": "#ffd6e7",
            "bubble_border": "#f5a8c8",
            "bubble_bg": "#fffafb",
            "reverse": True,
        },
        "takumi": {
            "icon_bg": "#d9f5d6",
            "bubble_border": "#9ed49a",
            "bubble_bg": "#fbfffb",
            "reverse": False,
        },
    }

    style = comment_styles.get(
        class_name,
        {
            "icon_bg": "#eeeeee",
            "bubble_border": "#cccccc",
            "bubble_bg": "#ffffff",
            "reverse": False,
        },
    )

    icon_html = (
        f'<img src="{icon_data_uri}" style="width:180%; height:180%; object-fit:cover; object-position:center 20%;">'
        if icon_data_uri
        else f'<span style="font-size:1.2rem; font-weight:800;">{escape(initial)}</span>'
    )

    flex_direction = "row-reverse" if style["reverse"] else "row"

    if style["reverse"]:
        arrow_style = (
            f"right:-8px;"
            f"border-right:1px solid {style['bubble_border']};"
            f"border-top:1px solid {style['bubble_border']};"
        )
    else:
        arrow_style = (
            f"left:-8px;"
            f"border-left:1px solid {style['bubble_border']};"
            f"border-bottom:1px solid {style['bubble_border']};"
        )

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: transparent;
    }}
    .comment-wrap {{
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 0;
        flex-direction: {flex_direction};
        width: 100%;
        box-sizing: border-box;
    }}
    .icon-area {{
        min-width: 90px;
        width: 90px;
        flex-shrink: 0;
        margin-top: 2px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
    }}
    .icon-circle {{
        width: 90px;
        height: 90px;
        border-radius: 50%;
        overflow: hidden;
        background: {style["icon_bg"]};
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .name {{
        margin-top: 6px;
        font-size: 16px;
        font-weight: 700;
        color: #444;
        line-height: 1.2;
        text-align: center;
        white-space: nowrap;
    }}
    .bubble {{
        position: relative;
        flex: 1;
        border: 1px solid {style["bubble_border"]};
        border-radius: 16px;
        background: {style["bubble_bg"]};
        padding: 14px 16px;
        box-sizing: border-box;
    }}
    .arrow {{
        position: absolute;
        {arrow_style}
        top: 16px;
        width: 14px;
        height: 14px;
        background: {style["bubble_bg"]};
        transform: rotate(45deg);
    }}
    .body {{
        font-size: 16px;
        line-height: 1.75;
        color: #333;
        word-break: break-word;
    }}
</style>
</head>
<body>
    <div class="comment-wrap">
        <div class="icon-area">
            <div class="icon-circle">
                {icon_html}
            </div>
            <div class="name">{escape(character)}</div>
        </div>

        <div class="bubble">
            <div class="arrow"></div>
            <div class="body">{escape(comment)}</div>
        </div>
    </div>
</body>
</html>
"""

    comment_height = max(210, min(430, 140 + (len(comment) // 14) * 28))

    # レイナは右アイコン配置の都合で、スマホ表示時に下余白が出やすいので少し詰める
    if class_name == "reina":
        comment_height = max(190, comment_height - 35)

    components.html(html, height=comment_height, scrolling=False)

def render_detail(work_id: str) -> None:
    client = get_supabase()
    row = fetch_public_work(work_id)

    if row is None:
        st.warning("作品が見つからないか、非公開になりました。")
        if st.button("一覧へ戻る", use_container_width=True):
            st.query_params.clear()
            st.rerun()
        return

    if st.button("← 一覧へ戻る", key=f"back-top-{work_id}", use_container_width=True):
        st.query_params.clear()
        st.rerun()

    title = clean_text(row.get("share_title"), "Untitled")
    poster_name = clean_text(row.get("poster_name"), "匿名の投稿者")
    published_at = format_date(row.get("created_at"))
    focus_point = clean_text(row.get("focus_point"))
    impression_score = clean_text(row.get("three_vis"), "-")
    image_url = get_image_url(client, row.get("image_path"))
    tags = normalize_tags(row.get("appeal_targets"))
    tags_html = make_tag_chips_html(tags)

    center_left, center_main, center_right = st.columns([1, 8, 1])
    with center_main:
        st.markdown('<div class="detail-main">', unsafe_allow_html=True)
        render_image(image_url, large=True)
        st.markdown('<div class="detail-image-note"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="detail-title">{escape(title)}</div>', unsafe_allow_html=True)

        if tags_html:
            st.markdown(tags_html, unsafe_allow_html=True)

        render_info_panel(poster_name, published_at)
        render_focus_box(focus_point)
        render_score_card(impression_score)

        st.markdown('<div class="comments-heading">3人コメント</div>', unsafe_allow_html=True)
        render_ai_comment_card("ジンさん", "ジ", clean_text(row.get("comment_jin")), "jin")
        render_ai_comment_card("レイナ", "レ", clean_text(row.get("comment_reina")), "reina")
        render_ai_comment_card("タクミ", "タ", clean_text(row.get("comment_takumi")), "takumi")

        st.markdown("<div style='margin-top: 1.2rem;'></div>", unsafe_allow_html=True)

        if st.button("← 一覧へ戻る", key=f"back-bottom-{work_id}", use_container_width=True):
            st.query_params.clear()
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

def render_contact_footer() -> None:
    st.markdown("""
<div style="
    margin-top: 28px;
    padding: 14px 12px;
    border-top: 1px solid #e5e7eb;
    color: #555;
    font-size: 14px;
    line-height: 1.7;
">
  <strong>お問い合わせ</strong><br>
  公開画像の削除依頼、不適切な画像の報告、その他のお問い合わせは、管理人までご連絡ください。<br>
  連絡先：threevibe.gallery@gmail.com
</div>
""", unsafe_allow_html=True)


def main() -> None:
    inject_css()
    render_header()

    work_id = st.query_params.get("work_id")
    if work_id:
        render_detail(str(work_id))
    else:
        render_hero_image()
        render_gallery()

    render_impression_app_link()
    render_contact_footer()


if __name__ == "__main__":
    main()