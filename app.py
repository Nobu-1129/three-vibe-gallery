
from __future__ import annotations

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

FIELD_CANDIDATES = {
    "id": ("id", "evaluation_id"),
    "image_path": ("image_path", "storage_path", "image_storage_path", "file_path"),
    "image_url": ("image_url", "public_image_url"),
    "author_name": ("author_name", "display_name", "creator_name", "user_name"),
    "title": ("title", "work_title", "image_title"),
    "three_vis": ("three_vis", "three_vis_score", "vis_score", "score_3vis", "3vis"),
    "highlight": ("highlight_note", "look_at_note", "focus_point", "kokomiteit_note"),
    "author_comment": ("author_comment", "free_comment", "creator_comment", "comment"),
    "comment_1": ("comment_1", "judge_comment_1", "evaluator_comment_1", "ai_comment_1"),
    "comment_2": ("comment_2", "judge_comment_2", "evaluator_comment_2", "ai_comment_2"),
    "comment_3": ("comment_3", "judge_comment_3", "evaluator_comment_3", "ai_comment_3"),
}


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
        .block-container {
            padding-top: 2rem;
            padding-bottom: 4rem;
            max-width: 1160px;
        }
        .brand-label {
            color: #667085;
            font-size: .92rem;
            font-weight: 650;
            margin-bottom: .35rem;
        }
        .gallery-title {
            font-size: 2.35rem;
            line-height: 1.08;
            font-weight: 820;
            margin-bottom: .35rem;
        }
        .gallery-title span {
            color: #454c5c;
            font-size: 1.35rem;
            font-weight: 720;
        }
        .gallery-lead {
            color: #333b49;
            font-size: 1.08rem;
            margin-bottom: .35rem;
        }
        .gallery-sub {
            color: #667085;
            margin-bottom: 1.4rem;
        }
        .meta {
            color: #667085;
            font-size: .88rem;
            margin-top: .25rem;
        }
        .score {
            display: inline-block;
            font-weight: 750;
            margin: .45rem 0;
        }
        .detail-copy {
            color: #333b49;
            line-height: 1.65;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)


def value(row: dict[str, Any], key: str, default: str = "") -> Any:
    for candidate in FIELD_CANDIDATES[key]:
        item = row.get(candidate)
        if item not in (None, ""):
            return item
    return default


def image_url(client: Client, row: dict[str, Any]) -> str | None:
    direct_url = value(row, "image_url", None)
    if direct_url:
        return str(direct_url)

    path = value(row, "image_path", None)
    if not path:
        return None

    path = str(path).lstrip("/")
    bucket_prefix = f"{BUCKET_NAME}/"
    if path.startswith(bucket_prefix):
        path = path[len(bucket_prefix) :]

    return client.storage.from_(BUCKET_NAME).get_public_url(path)


@st.cache_data(ttl=60)
def fetch_public_works(limit: int = PAGE_SIZE) -> list[dict[str, Any]]:
    client = get_supabase()
    response = (
        client.table(TABLE_NAME)
        .select("*")
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
        .select("*")
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


def render_card(client: Client, row: dict[str, Any]) -> None:
    url = image_url(client, row)
    title = value(row, "title", "Untitled")
    author = value(row, "author_name", "匿名の投稿者")
    score = value(row, "three_vis", "-")
    highlight = value(row, "highlight", "")
    author_comment = value(row, "author_comment", "")
    work_id = value(row, "id", "")

    with st.container(border=True):
        if url:
            st.image(url, use_container_width=True)
        else:
            st.info("画像を表示できません")

        st.subheader(str(title))
        st.markdown(f'<div class="meta">by {author}</div>', unsafe_allow_html=True)
        st.markdown(f'<span class="score">3VIS: {score}</span>', unsafe_allow_html=True)

        if highlight:
            st.caption("ココ見てほしい")
            st.write(str(highlight))
        if author_comment:
            st.caption("投稿者フリーコメント")
            st.write(str(author_comment))

        if st.button("詳細を見る", key=f"detail-{work_id}", use_container_width=True):
            st.query_params["work_id"] = str(work_id)
            st.rerun()


def render_gallery() -> None:
    client = get_supabase()
    works = fetch_public_works()

    if not works:
        st.info("公開中の作品はまだありません。")
        return

    columns = st.columns(3)
    for index, row in enumerate(works):
        with columns[index % 3]:
            render_card(client, row)


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

    title = value(row, "title", "Untitled")
    author = value(row, "author_name", "匿名の投稿者")
    score = value(row, "three_vis", "-")
    url = image_url(client, row)

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        if url:
            st.image(url, use_container_width=True)
        else:
            st.info("画像を表示できません")

    with right:
        st.title(str(title))
        st.markdown(f"**投稿者名:** {author}")
        st.markdown(f"**3VIS:** {score}")

        highlight = value(row, "highlight", "")
        if highlight:
            st.markdown("#### ココ見てほしい")
            st.markdown(f'<div class="detail-copy">{highlight}</div>', unsafe_allow_html=True)

        author_comment = value(row, "author_comment", "")
        if author_comment:
            st.markdown("#### 投稿者フリーコメント")
            st.markdown(f'<div class="detail-copy">{author_comment}</div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 3人コメント")
    comment_cols = st.columns(3)
    comments = [value(row, "comment_1", ""), value(row, "comment_2", ""), value(row, "comment_3", "")]
    for index, comment in enumerate(comments):
        with comment_cols[index]:
            with st.container(border=True):
                st.markdown(f"**Comment {index + 1}**")
                st.write(str(comment) if comment else "コメントなし")


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
