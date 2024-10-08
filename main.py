import os
import time
import argparse
from instaloader import NodeIterator
from instaloader.structures import Profile
from instaloader.instaloader import Instaloader

class Args:
    username: str
    output: str

def login_instagram(username: str) -> Instaloader | None:
    loader = Instaloader()
    try:
        loader.load_session_from_file(username, filename=f"session-{username}") 
        print(f"Session loaded for {username} from session!")
        return loader
    except FileNotFoundError:
        os.system(f"instaloader --login {username} --sessionfile session-{username}")
        return login_instagram(username)

def fetch_following(loader: Instaloader, username: str) -> NodeIterator[Profile]:
    try:
        profile = Profile.from_username(loader.context, username)
        following = profile.get_followees()
        print(f"Found {len(following)} users you are following.")
        return following
    except Exception as e:
        print(f"An error occurred while fetching the following data: {e}")
        return set()

def fetch_followers(loader: Instaloader, username: str) -> NodeIterator[Profile]:
    try:
        profile = Profile.from_username(loader.context, username)
        followers = profile.get_followers()
        print(f"Found {len(followers)} users following you.")
        return followers
    except Exception as e:
        print(f"An error occurred while fetching the followers data: {e}")
        return set()

def find_non_followers(followers: set[str], following: set[str]) -> set[str]:
    return following - followers

def save_results(non_followers: set[str], output_file: str) -> None:
    try:
        with open(output_file, 'w') as f:
            f.write('\n'.join(non_followers))
        print(f"Results saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while saving results: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Instagram Followers Checker")
    parser.add_argument('--username', required=True, help="Instagram username")
    parser.add_argument(
        '--output', 
        default="non_followers.txt", 
        help="Output file for non-followers"
    )

    args = parser.parse_args(namespace=Args())

    username: str = args.username
    output_file: str = args.output

    loader: Instaloader | None = login_instagram(username)
    if not loader:
        return

    print("Fetching following list...")
    following: set[str] = fetch_following(loader, username)

    # Add delay to avoid rate limits
    time.sleep(150)

    print("Fetching followers list...")
    followers: set[str] = fetch_followers(loader, username)

    if not followers or not following:
        print("No followers or following data was retrieved.")
        return

    non_followers: set[str] = find_non_followers(followers, following)

    if non_followers:
        print("These users are not following you back:")
        for user in non_followers:
            print(user)
        
        save_results(non_followers, output_file)
    else:
        print("Everyone you follow is following you back!")

if __name__ == "__main__":
    main()
