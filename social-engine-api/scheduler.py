
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

import crud
from publisher import publish_post


# =========================================
# SCHEDULER INSTANCE
# =========================================

scheduler = BackgroundScheduler()


# =========================================
# CHECK SCHEDULED POSTS
# =========================================

def check_scheduled_posts():

    posts = crud.get_scheduled_posts()

    current_time = datetime.now()

    for post in posts:

        # Only pending posts
        if post["status"] == "pending":

            scheduled_time = datetime.strptime(
                post["scheduled_time"],
                "%Y-%m-%d %H:%M:%S"
            )

            # Publish when time reached
            if current_time >= scheduled_time:

                print(f"Publishing post {post['post_id']}")

                # Publish post
                publish_post(post["post_id"])

                # Update scheduled post status
                crud.update_scheduled_post(
                    post["id"],
                    {
                        "scheduled_time": post["scheduled_time"],
                        "status": "completed"
                    }
                )

                # Update post status
                crud.update_post(
                    post["post_id"],
                    {
                        "topic": None,
                        "caption": None,
                        "hashtags": None,
                        "image_path": None,
                        "template_id": None,
                        "platform": None,
                        "status": "published",
                        "published_at": str(current_time)
                    }
                )

                # Save publishing history
                crud.create_publishing_history({

                    "post_id": post["post_id"],

                    "platform": "instagram",

                    "status": "success",

                    "response": "Post published successfully"
                })

                print(f"Post {post['post_id']} completed")


# =========================================
# START SCHEDULER
# =========================================

def start_scheduler():

    scheduler.add_job(
        check_scheduled_posts,
        "interval",
        seconds=30
    )

    scheduler.start()

    print("Scheduler started...")

