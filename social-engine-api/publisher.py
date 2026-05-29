
import crud


def publish_post(post_id):

    print(f"Publishing post {post_id}")

    crud.update_post(
        post_id,
        {
            "topic": None,
            "caption": None,
            "hashtags": None,
            "image_path": None,
            "template_id": None,
            "platform": None,
            "status": "published",
            "published_at": None
        }
    )

    print("Post published successfully")

    return True

