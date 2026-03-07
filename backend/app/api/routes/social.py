import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.social import Post, Comment, Like, PostType
from app.models.user import User
from app.schemas.social import PostCreate, PostRead, CommentCreate, CommentRead
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter

router = APIRouter()


@router.get("/feed", response_model=list[PostRead])
@limiter.limit("30/minute")
async def get_feed(
    request,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    post_type: str | None = Query(None, pattern=r"^(result|medal|video|tournament|training|general)$"),
):
    query = select(Post).where(Post.is_published == True)

    if post_type:
        query = query.where(Post.post_type == post_type)

    query = query.order_by(Post.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    posts = result.scalars().all()

    # Enrich with author info
    enriched = []
    for post in posts:
        author_result = await db.execute(select(User).where(User.id == post.author_id))
        author = author_result.scalar_one_or_none()
        enriched.append(
            PostRead(
                id=post.id,
                author_id=post.author_id,
                author_name=author.full_name if author else None,
                author_avatar=author.avatar_url if author else None,
                post_type=post.post_type.value,
                content=post.content,
                media_urls=post.media_urls,
                hashtags=post.hashtags,
                event_id=post.event_id,
                match_id=post.match_id,
                like_count=post.like_count,
                comment_count=post.comment_count,
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
        )
    return enriched


@router.post("/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = Post(
        author_id=user.id,
        post_type=PostType(data.post_type),
        content=data.content,
        media_urls=data.media_urls,
        hashtags=data.hashtags,
        event_id=data.event_id,
        match_id=data.match_id,
    )
    db.add(post)
    await db.flush()
    await db.refresh(post)

    return PostRead(
        id=post.id,
        author_id=post.author_id,
        author_name=user.full_name,
        author_avatar=user.avatar_url,
        post_type=post.post_type.value,
        content=post.content,
        media_urls=post.media_urls,
        hashtags=post.hashtags,
        event_id=post.event_id,
        match_id=post.match_id,
        like_count=0,
        comment_count=0,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.post("/posts/{post_id}/like", status_code=status.HTTP_200_OK)
async def toggle_like(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check post exists
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # Check if already liked
    like_result = await db.execute(
        select(Like).where(Like.post_id == post_id, Like.user_id == user.id)
    )
    existing_like = like_result.scalar_one_or_none()

    if existing_like:
        await db.delete(existing_like)
        post.like_count = max(0, post.like_count - 1)
        return {"liked": False, "like_count": post.like_count}
    else:
        like = Like(post_id=post_id, user_id=user.id)
        db.add(like)
        post.like_count += 1
        return {"liked": True, "like_count": post.like_count}


@router.get("/posts/{post_id}/comments", response_model=list[CommentRead])
@limiter.limit("30/minute")
async def get_comments(
    request,
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    query = (
        select(Comment)
        .where(Comment.post_id == post_id, Comment.is_published == True)
        .order_by(Comment.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    comments = result.scalars().all()

    enriched = []
    for comment in comments:
        author_result = await db.execute(select(User).where(User.id == comment.author_id))
        author = author_result.scalar_one_or_none()
        enriched.append(
            CommentRead(
                id=comment.id,
                post_id=comment.post_id,
                author_id=comment.author_id,
                author_name=author.full_name if author else None,
                author_avatar=author.avatar_url if author else None,
                parent_id=comment.parent_id,
                content=comment.content,
                created_at=comment.created_at,
            )
        )
    return enriched


@router.post("/posts/{post_id}/comments", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: uuid.UUID,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Check post exists
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        author_id=user.id,
        content=data.content,
        parent_id=data.parent_id,
    )
    db.add(comment)
    post.comment_count += 1
    await db.flush()
    await db.refresh(comment)

    return CommentRead(
        id=comment.id,
        post_id=comment.post_id,
        author_id=comment.author_id,
        author_name=user.full_name,
        author_avatar=user.avatar_url,
        parent_id=comment.parent_id,
        content=comment.content,
        created_at=comment.created_at,
    )
