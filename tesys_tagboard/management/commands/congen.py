import re
from itertools import islice
from pathlib import Path
from random import choice
from random import choices
from random import randint
from random import sample
from typing import TYPE_CHECKING
from typing import Annotated

import magic
import typer
from django.core.files.uploadedfile import UploadedFile
from django_typer.management import Typer
from PIL import UnidentifiedImageError
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import track

from tesys_tagboard.enums import MediaCategory
from tesys_tagboard.enums import RatingLevel
from tesys_tagboard.enums import SupportedMediaTypes
from tesys_tagboard.enums import TagCategory
from tesys_tagboard.models import Audio
from tesys_tagboard.models import Collection
from tesys_tagboard.models import Comment
from tesys_tagboard.models import Image
from tesys_tagboard.models import Post
from tesys_tagboard.models import Tag
from tesys_tagboard.models import TagAlias
from tesys_tagboard.models import Video
from tesys_tagboard.models import add_tag_history
from tesys_tagboard.models import update_tag_post_counts
from tesys_tagboard.users.models import User

if TYPE_CHECKING:
    from collections.abc import Iterable

    from django.db.models import QuerySet


DEFAULT_USERNAMES = ["user1", "user2", "user3", "mod1", "mod2", "mod3"]

# Text content for filling titles, comments, etc.
CONTENT_PARAGRAPHS = [
    "Having had some time at my disposal when in London, I had visited the British Museum, and made search among the books and maps in the library regarding Transylvania; it had struck me that some foreknowledge of the country could hardly fail to have some importance in dealing with a nobleman of that country. I find that the district he named is in the extreme east of the country, just on the borders of three states, Transylvania, Moldavia and Bukovina, in the midst of the Carpathian mountains; one of the wildest and least known portions of Europe. I was not able to light on any map or work giving the exact locality of the Castle Dracula, as there are no maps of this country as yet to compare with our own Ordnance Survey maps; but I found that Bistritz, the post town named by Count Dracula, is a fairly well-known place. I shall enter here some of my notes, as they may refresh my memory when I talk over my travels with Mina.",  # noqa: E501
    "In the population of Transylvania there are four distinct nationalities: Saxons in the South, and mixed with them the Wallachs, who are the descendants of the Dacians; Magyars in the West, and Szekelys in the East and North. I am going among the latter, who claim to be descended from Attila and the Huns. This may be so, for when the Magyars conquered the country in the eleventh century they found the Huns settled in it. I read that every known superstition in the world is gathered into the horseshoe of the Carpathians, as if it were the centre of some sort of imaginative whirlpool; if so my stay may be very interesting. (Mem., I must ask the Count all about them.)",  # noqa: E501
    "I did not sleep well, though my bed was comfortable enough, for I had all sorts of queer dreams. There was a dog howling all night under my window, which may have had something to do with it; or it may have been the paprika, for I had to drink up all the water in my carafe, and was still thirsty. Towards morning I slept and was wakened by the continuous knocking at my door, so I guess I must have been sleeping soundly then. I had for breakfast more paprika, and a sort of porridge of maize flour which they said was “mamaliga,” and egg-plant stuffed with forcemeat, a very excellent dish, which they call “impletata.” (Mem., get recipe for this also.) I had to hurry breakfast, for the train started a little before eight, or rather it ought to have done so, for after rushing to the station at 7:30 I had to sit in the carriage for more than an hour before we began to move. It seems to me that the further east you go the more unpunctual are the trains. What ought they to be in China?",  # noqa: E501
    "All day long we seemed to dawdle through a country which was full of beauty of every kind. Sometimes we saw little towns or castles on the top of steep hills such as we see in old missals; sometimes we ran by rivers and streams which seemed from the wide stony margin on each side of them to be subject to great floods. It takes a lot of water, and running strong, to sweep the outside edge of a river clear. At every station there were groups of people, sometimes crowds, and in all sorts of attire. Some of them were just like the peasants at home or those I saw coming through France and Germany, with short jackets and round hats and home-made trousers; but others were very picturesque. The women looked pretty, except when you got near them, but they were very clumsy about the waist. They had all full white sleeves of some kind or other, and most of them had big belts with a lot of strips of something fluttering from them like the dresses in a ballet, but of course there were petticoats under them. The strangest figures we saw were the Slovaks, who were more barbarian than the rest, with their big cow-boy hats, great baggy dirty-white trousers, white linen shirts, and enormous heavy leather belts, nearly a foot wide, all studded over with brass nails. They wore high boots, with their trousers tucked into them, and had long black hair and heavy black moustaches. They are very picturesque, but do not look prepossessing. On the stage they would be set down at once as some old Oriental band of brigands. They are, however, I am told, very harmless and rather wanting in natural self-assertion.",  # noqa: E501
    "It was on the dark side of twilight when we got to Bistritz, which is a very interesting old place. Being practically on the frontier—for the Borgo Pass leads from it into Bukovina—it has had a very stormy existence, and it certainly shows marks of it. Fifty years ago a series of great fires took place, which made terrible havoc on five separate occasions. At the very beginning of the seventeenth century it underwent a siege of three weeks and lost 13,000 people, the casualties of war proper being assisted by famine and disease.",  # noqa: E501
    "Count Dracula had directed me to go to the Golden Krone Hotel, which I found, to my great delight, to be thoroughly old-fashioned, for of course I wanted to see all I could of the ways of the country. I was evidently expected, for when I got near the door I faced a cheery-looking elderly woman in the usual peasant dress—white undergarment with long double apron, front, and back, of coloured stuff fitting almost too tight for modesty. When I came close she bowed and said, “The Herr Englishman?” “Yes,” I said, “Jonathan Harker.” She smiled, and gave some message to an elderly man in white shirt-sleeves, who had followed her to the door. He went, but immediately returned with a letter",  # noqa: E501
]
CONTENT_SENTENCES = [
    s.strip() + "." for s in re.split(r"[.?]\s", "\n".join(CONTENT_PARAGRAPHS))
]
CONTENT_WORDS = list(set(re.findall(r"[a-zA-Z]+", "\n".join(CONTENT_PARAGRAPHS))))

USER_NAME_BASES = [
    "elif",
    "gunther",
    "jade",
    "lilly",
    "ricardo",
    "sandy",
    "simon",
    "wendy",
    "zorian",
]
TAG_NAME_BASES = [
    "red",
    "blue",
    "violet",
    "evergreen",
    "cobalt",
    "kobold",
    "mimic",
    "bugbear",
    "vorpal_rat",
    "hyena",
    "warthog",
]
TAG_CATEGORY_SHORTCODES = [tc.value.shortcode for tc in TagCategory]


app = Typer()


@app.command()
def main(  # noqa: PLR0913
    media_dir: Annotated[str, typer.Argument()],
    max_tags: Annotated[
        int,
        typer.Option(
            "--max-tags", "-t", help="The maximum number of tags to randomly generate."
        ),
    ] = 500,
    max_users: Annotated[
        int,
        typer.Option(
            "--max-users",
            "-u",
            help="The maximum number of users to randomly generate.",
        ),
    ] = 200,
    max_posts: Annotated[
        int,
        typer.Option(
            "--max-posts",
            "-p",
            help="The maximum number of posts to randomly generate.",
        ),
    ] = 500,
    max_collections: Annotated[
        int,
        typer.Option(
            "--max-collections",
            "-c",
            help="The maximum number of collections to randomly generate.",
        ),
    ] = 50,
    max__posts_per_collection: Annotated[
        int,
        typer.Option(
            help="The maximum number of posts to link to any single collection"
        ),
    ] = 50,
):
    """
    A command to create demo data for testing the app. Media files must be loaded from
    disk. The provided `media_dir` will be searched recursively for any supported files
    and create posts from them. All other data such as Tags, Comments, Collections, and
    Users will be generated randomly with options to adjust the thresholds.
    """
    default_users = [User(username=name) for name in DEFAULT_USERNAMES]
    User.objects.bulk_create(default_users, ignore_conflicts=True)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Deleting old data...", total=None)
        Tag.objects.all().delete()
        TagAlias.objects.all().delete()
        Post.objects.all().delete()
        User.objects.exclude(pk__in=(u.pk for u in default_users)).delete()
        Collection.objects.all().delete()
    print("Old data deleted.")

    create_random_users(max_users)

    create_random_tags(max_tags)

    create_random_tag_aliases(Tag.objects.all())

    media_files = get_media_files_from_disk(Path(media_dir))
    create_random_posts(media_files, user_select_max=50, max_posts=max_posts)

    create_random_post_collections(Post.objects.all(), max_collections=50)


def create_random_users(n: int = 50, suffix_min: int = 1, suffix_max: int = 99999):
    """Create `n` randomized Users
    Note each user's password is the same as their username
    """
    n = min(n, 10_000)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Creating random users...", total=None)
        random_user_names = {
            f"{name}_{randint(suffix_min, suffix_max)}"
            for name in choices(USER_NAME_BASES, k=n)
        }
        users = [User(username=name, password=name) for name in random_user_names]
        User.objects.bulk_create(users, ignore_conflicts=True)
    print(f"Created {len(users)} users.")


def create_random_tags(n: int = 500, suffix_min: int = 1, suffix_max: int = 99999):
    """Create `n` randomized Tags"""
    n = min(n, 10_000)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Creating random tags...", total=None)
        random_tag_names = {
            f"{name}_{randint(suffix_min, suffix_max)}"
            for name in choices(TAG_NAME_BASES, k=n)
        }
        tags = [
            Tag(name=name, category=choice(TAG_CATEGORY_SHORTCODES))
            for name in random_tag_names
        ]
        Tag.objects.bulk_create(tags, ignore_conflicts=True)
    print(f"Created {len(tags)} tags.")


def create_random_tag_aliases(tags: QuerySet[Tag], percent: float = 0.1):
    """Create TagAliases for the given set of tags
    percent: percent of Tags to receive an alias
    """

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Creating random tag aliases...", total=None)
        picked_tags = choices(tags, k=int(percent * len(tags)))
        tag_aliases = [
            TagAlias(name=f"alias_{i}_{tag.name}", tag=tag)
            for i, tag in enumerate(picked_tags)
        ]
        TagAlias.objects.bulk_create(tag_aliases, ignore_conflicts=True)
    print(f"Created {len(tag_aliases)} tag aliases.")


def create_random_post_collections(
    posts: QuerySet[Post],
    max_collections: int = 100,
    max_posts_per_collection: int = 50,
):
    """Create collections with randomly assigned posts"""
    collections = []
    collection_posts = []
    user_options = list(User.objects.all())
    post_options = list(posts)
    for _ in range(max_collections):
        collection = Collection(
            user=choice(user_options),
            name=" ".join(choices(CONTENT_WORDS, k=randint(2, 8))),
            desc=" ".join(choices(CONTENT_WORDS, k=randint(4, 15))),
        )
        collections.append(collection)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Creating collections...", total=None)
        created_collections = Collection.objects.bulk_create(collections)

    print(f"Created {len(created_collections)} collections.")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Linking collections to posts...", total=None)

        def get_random_post_ids():
            return [
                s.pk
                for s in sample(post_options, k=randint(0, max_posts_per_collection))
            ]

        collection_posts = []
        for collection in created_collections:
            collection_posts.extend(
                [
                    Collection.posts.through(
                        collection_id=collection.pk, post_id=post_id
                    )
                    for post_id in get_random_post_ids()
                ]
            )

        created_collection_posts = Collection.posts.through.objects.bulk_create(
            collection_posts
        )
    print(f"Added {len(created_collection_posts)} posts to collections.")


def create_random_posts(  # noqa: C901, PLR0912, PLR0915
    media_files: Iterable[Path], user_select_max=100, max_posts=1000
):
    tag_options = list(Tag.objects.all())
    users = User.objects.all()
    uploaders = choices(users, k=user_select_max)
    posts = []
    comments = []
    media_objects = []
    media_files_list = list(media_files)

    media_files_sample = sample(
        media_files_list, k=min(len(media_files_list), max_posts)
    )
    for file in track(
        media_files_sample,
        description="Creating posts from media files...",
    ):
        m = magic.from_file(file, mime=True)
        if smt := SupportedMediaTypes.find(m):
            if media_type := SupportedMediaTypes.find(smt.value.get_template()):
                post = Post(
                    title=" ".join(choices(CONTENT_WORDS, k=randint(1, 10))),
                    uploader=choice(uploaders),
                    rating_level=choice(RatingLevel.choices())[0],
                    src_url=choice(CONTENT_WORDS) + ".example.com",
                    type=media_type.name,
                )

                comment_texts = [
                    " ".join(choices(CONTENT_SENTENCES, k=randint(1, 10)))
                    for _ in range(randint(0, 10))
                ]

                comments.extend(
                    [
                        Comment(post=post, user=choice(users), text=text)
                        for text in comment_texts
                    ]
                )

                media_object = None
                match smt.value.category:
                    case MediaCategory.AUDIO:
                        fp = file.open("rb")
                        media_object = Audio(
                            file=UploadedFile(UploadedFile(fp)), orig_name=file.name
                        )
                    case MediaCategory.IMAGE:
                        try:
                            fp = file.open("rb")
                            media_object = Image(
                                file=UploadedFile(fp), orig_name=file.name
                            )
                        except UnidentifiedImageError:
                            print("The image file couldn't be identified by PIL")
                            print(f"See the file at {file.resolve()}")
                    case MediaCategory.VIDEO:
                        fp = file.open("rb")
                        media_object = Video(
                            file=UploadedFile(UploadedFile(fp)), orig_name=file.name
                        )

                if media_object:
                    media_object.post = post
                    media_objects.append(media_object)

                posts.append(post)
            else:
                print(f"The file type of '{file}' is not supported")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Creating posts...", total=None)
        created_posts = Post.objects.bulk_create(posts)
    print(f"Created {len(created_posts)} posts.")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Adding tags to posts...", total=None)

        post_tags = []

        def get_random_tag_ids():
            return [s.pk for s in sample(tag_options, k=randint(0, 25))]

        for post in created_posts:
            post_tags.extend(
                [
                    Post.tags.through(post_id=post.pk, tag_id=tag_id)
                    for tag_id in get_random_tag_ids()
                ]
            )

        Post.tags.through.objects.bulk_create(post_tags)
    print("Tags added to posts.")

    for post in track(created_posts, description="Updating posts' tag histories..."):
        add_tag_history(post.tags.all(), post, post.uploader)

    for post in track(created_posts, description="Updating posts' source histories..."):
        post.save_with_src_history(post.uploader, post.src_url)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Adding comments to posts...", total=None)
        Comment.objects.bulk_create(comments)
    print("Comments added to posts.")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Updating tag post counts", total=None)
        update_tag_post_counts()
    print("Tag post counts updated.")

    for post in track(
        created_posts, description="Adding parent and child post links..."
    ):
        for child_post in choices(created_posts, k=randint(0, 5)):
            child_post.parent = post
            child_post.save()
    print("Parent and child post links added.")

    for obj in track(
        media_objects,
        description="Saving media files to database and generating thumbnails...",
    ):
        try:
            obj.save()
        except OSError as e:
            print(e)
            continue
    print(f"Saved {len(media_objects)} media files.")


def get_media_files_from_disk(
    path: Path, *, recursive: bool = True, max_files: int = 1000
) -> Iterable[Path]:
    """Imports media (audios, images, or videos) from disk"""
    media_files = []
    if recursive:
        media_files = (f for f in path.glob("**") if f.is_file())
    else:
        media_files = (f for f in path.glob("*") if f.is_file())

    return islice(media_files, max_files)
