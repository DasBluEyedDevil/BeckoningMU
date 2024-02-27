from evennia import default_cmds
from evennia.utils import list_to_string
from evennia.utils.ansi import ANSIString
# update this import to match your project structure
from .models import Board, Post, Comment
# get the AccountDB class from the engine
from evennia.accounts.models import AccountDB
from datetime import datetime
from evennia.commands.default.muxcommand import MuxCommand


class CmdBBS(default_cmds.MuxCommand):
    """
    This method is designed to handle multiple commands related to an interactive message board functionality. The usage is as follows:

    Usage:
        +bbs: List all accessible boards.
        +bbs: <board>[/title]: View all posts on the specified board. If a title is provided, only posts with id will be displayed.
        +bbs/boards: List all boards.
        +bbs/view <board_name>: View all posts on the specified board.
        +bbs/read <post_id>: Read a specific post and its comments.
        +bbs/post <board_name> = <post_title>/<post_body>: Post a new message on the specified board.
        +bbs/comment <post_id> = <comment_body>: Comment on a specific post.
        +bbs/deletepost <post_id>: Delete a specific post.
        +bbs/deletecomment <comment_id>: Delete a specific comment.
        +bbs/createboard <board_name> = <read_perm>/<write_perm>: Create a new board with specified read and write permissions.
        +bbs/editboard <board_name> = <read_perm>/<write_perm>: Edit the read and write permissions of an existing board.
        +bbs/deleteboard <board_name>: Delete an existing board.
        +bbs/read <group_name>: Mark all unread posts in a group as read.
        +bbs/catchup <group_name>: Mark all posts in a group as read.
        +bbs/scan: List the number of unread posts in each group.
        +bbs/post/split <args>: Post a message in multiple parts.
        +bbs/leave <group_name>: Remove the player from a group.
        +bbs/join <group_name>: Add the player to a group.

    If an invalid command is provided, it sends a message to the caller about it.
    """

    key = "+bbs"
    aliases = ["+BBS", "bbs", "+bb", "bb", "bbview", "bbread"]
    lock = "cmd:all()"
    help_category = "Boards"

    """
    Read boards or posts on the BBS.

    Usage:
      bbread             - List all boards
      bbread <board_id>  - View board by id
      bbread <board_name>- View board by name
      bbread <board_id>/<post_id>   - Read post by board id and post id
      bbread <board_name>/<post_id> - Read post by board name and post id
      bbread <board_name>/<post_name> - Read post by board name and post name
    """
    def list_boards(self):
        "List all boards."
        boards = Board.objects.all()
        output = "|b=|n" * 78 + "\n"
        output += "|wID|n".ljust(4)
        output += "  |wBoard Name|n".ljust(35)
        output += "      |wLast Post|n".ljust(22)
        output += "           |w# of Messages".ljust(13) + "\n"
        output += "|b=|n" * 78 + "\n"
        for board in boards:
            if board.read_perm == "all" or self.caller.check_permstring(board.read_perm):
                last_post = board.posts.last()
                formatted_datetime = "None"
                if last_post:
                    formatted_datetime = last_post.created_at.strftime("%Y-%m-%d")
                num_posts = board.posts.count()
                output += str(board.id).ljust(4)
                output += board.name[:34].ljust(35)
                output += formatted_datetime.ljust(22)
                output += str(num_posts).rjust(9) + "\n"
        output += "|b=|n" * 78
        self.caller.msg(output)

    def view_board(self, board):
        "View specific board."
        # Format and send board posts
        posts = board.posts.all()
        output = format_board_posts_output(self, posts, board)
        self.caller.msg(output)
"""
    def read_post(self, board_identifier, post_arg):
        
        #Attempts to find and display a post based on a board identifier (name or ID) and a post ID.
        
        try:
            # Attempt to find the board by ID or name
            if str(board_identifier).isdigit():
                board = Board.objects.get(id=int(board_identifier))
            else:
                board = Board.objects.get(name__iexact=board_identifier)
        except Board.DoesNotExist:
            self.caller.msg("Board not found.")
            return
    
        # Now proceed with your existing logic to find and display the post
        # For example, using the logic previously discussed:
        try:
            post_id = int(post_arg)  # Assuming post_arg is the post ID as a string
            post = board.posts.get(id=post_id)
            # Format and send post details to the caller
            output = self.format_post(post)  # You need to implement this method
            self.caller.msg(output)
        except (ValueError, Post.DoesNotExist):
            self.caller.msg("Post not found.")
"""

    
    def read_post(self, board, post_arg):
        "Read specific post."
        try:
            post = board.posts.get(id=post_arg)
        except (Post.DoesNotExist, ValueError):
            try:
                post = board.posts.get(title__iexact=post_arg)
            except Post.DoesNotExist:
                self.caller.msg("Post not found.")
                return
        # Format and send post
        output = format_post(self, post)
        self.caller.msg(output)

    def get_name(self, name):
        try:
            try:
                board = Board.objects.get(name=name)
            except:
                board = Board.objects.get(id=name)

            if not self.caller.check_permstring(board.write_perm):
                self.caller.msg(
                    "You do not have permission to delete this board.")
                return
        except:
            self.caller.msg("Board not found.")
            return

        return board

    def func(self):
        args = self.args.strip()

        # Split arguments
        try:
            board_arg, post_arg = args.split("/", 1)
        except ValueError:
            board_arg, post_arg = args, None

        # No arguments - List all boards
        if not board_arg:
            self.list_boards()
            return

        # Board argument present - Attempt to view board or read post
        try:
            board = Board.objects.get(id=board_arg)
        except (Board.DoesNotExist, ValueError):
            try:
                board = Board.objects.get(name__iexact=board_arg)
            except Board.DoesNotExist:
                self.caller.msg("Board not found.")
                return

        # Board found - Check for post argument
        if post_arg:
            self.read_post(board, post_arg)
        else:
            self.view_board(board)

        # Handle different commands
        if "boards" in self.switches:
            self.list_boards()
        elif "view" in self.switches:
            self.view_board(self.args)
        elif "read" in self.switches:
            self.read_post(self.args)
        elif "post" in self.switches:
            board_name, post_content = self.args.split("=")
            post_title, post_body = post_content.split("/")
            self.post(board_name, post_title, post_body)
        elif "comment" in self.switches:
            post_id, comment_body = self.args.split("=")
            self.comment(post_id, comment_body)
        elif "deletepost" in self.switches:
            self.delete_post(self.args)
        elif "deletecomment" in self.switches:
            self.delete_comment(self.args)
        elif "createboard" in self.switches:
            try:
                board_name, perms = self.args.split("=")
                read_perm, write_perm = perms.split("/")
            except ValueError:
                board_name = self.args
                read_perm = "all"
                write_perm = "all"

            self.create_board(board_name, read_perm, write_perm)
        elif "editboard" in self.switches:
            board_name, perms = self.args.split("=")
            read_perm, write_perm = perms.split("/")
            self.edit_board(board_name, read_perm, write_perm)
        elif "deleteboard" in self.switches:
            self.delete_board(self.args)
        elif 'read' in self.switches:
            self.read_all_unread(self.args)
        elif 'catchup' in self.switches:
            self.mark_all_as_read(self.args)
        elif 'scan' in self.switches:
            self.scan_for_unread()
        elif 'post/split' in self.switches:
            self.split_post(self.args)
        elif 'leave' in self.switches:
            self.leave_group(self.args)
        elif 'join' in self.switches:
            self.join_group(self.args)

    def edit_board(self, board_name, read_perm, write_perm):

        # edit requires at least builder.
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("You do not have permission to edit boards.")
            return

        "Edit a board."
        try:
            board = Board.objects.get(name=board_name)
        except Board.DoesNotExist:
            board = Board.objects.get(id=board_name)
        except Board.DoesNotExist:
            self.caller.msg("No board by that name or ID exists.")
            return

        if not self.caller.check_permstring(board.write_perm):
            self.caller.msg("You do not have permission to edit this board.")
            return

        board.read_perm = read_perm
        board.write_perm = write_perm
        board.save()

        self.caller.msg("Edited board {}.".format(board.name))

    def delete_board(self, board_name):
        "Delete a board."
        # delete requires at least builder.
        if not self.caller.check_permstring("Builder"):
            self.caller.msg("You do not have permission to delete boards.")
            return
        try:
            try:
                board = Board.objects.get(name=board_name)
            except:
                board = Board.objects.get(id=board_name)

            if not self.caller.check_permstring(board.write_perm):
                self.caller.msg(
                    "You do not have permission to delete this board.")
                return
        except Board.DoesNotExist:
            self.caller.msg("No board by that name or ID exists.")
            return

        self.caller.msg("Deleted board {}.".format(board.name))
        board.delete()

    def create_board(self, board_name, read_perm, write_perm):
        "Create a new board."
        if not self.caller.check_permstring("builders"):
            self.caller.msg(
                "You do not have permission to create a new board.")
            return
        # check if the board already exists.'
        if Board.objects.filter(name=board_name).exists():
            self.caller.msg("That board already exists.")
            return

        Board.objects.create(
            name=board_name, read_perm=read_perm, write_perm=write_perm)
        self.caller.msg("Created board {}.".format(board_name))

    def post(self, board_name, post_title, post_body):
        try:
            board = Board.objects.get(name=board_name)
            # Assuming self.caller is a username, find the AccountDB instance
            # Adjust this line if self.caller represents something else, like a user ID
            author = AccountDB.objects.get(username=self.caller)
            
            new_post = Post(author=author, board=board, title=post_title, body=post_body)
            new_post.save()
            self.caller.msg("Your post has been created successfully.")
            return  # Ensure no further code is executed
        except Board.DoesNotExist:
            self.caller.msg(f"Board named '{board_name}' does not exist.")
        except AccountDB.DoesNotExist:
            self.caller.msg("Author account not found.")
        except Exception as e:
            print(f"Error creating post: {e}")
            self.caller.msg(f"An error occurred while creating the post: {e}")
        else:
            print("User does not have permission to post.")
            self.caller.msg("You do not have permission to post to this board.")

    def comment(self, post_id, comment_body):
        """
        Comment on a post.
        """
        # Split the post_identifier into board_identifier and post_id
        try:
            board_id, post_id = post_id.split("/")
        except ValueError:
            self.caller.msg("Usage: comment <board_id or board_name>/<post_id> = <comment_body>")
            return
        
        # Attempt to find the board by ID or name
        try:
            board = Board.objects.get(id=board_id)
        except Board.DoesNotExist:
            try:
                board = Board.objects.get(name__iexact=board_id)
            except Board.DoesNotExist:
                self.caller.msg("Board not found.")
                return
        
        # Attempt to find the post
        try:
            post = board.posts.get(id=post_id)
        except Post.DoesNotExist:
            self.caller.msg("Post not found.")
            return        
        
        # Check if the user has permission to read the post (hence comment)
        if not (post.read_perm == 'all' or self.caller.check_permstring(post.read_perm)):
            self.caller.msg("You do not have permission to comment on this post.")
            return
        
        # Assuming self.caller.account returns the associated AccountDB instance
        author = self.caller.account
        
        # Create the comment
        Comment.objects.create(author=author, post=post, body=comment_body)
        self.caller.msg("Comment added successfully.")
        
        # nofity all connected players who have either posted the post or commented on it.
        for player in AccountDB.objects.get_connected_accounts():
            if player.check_permstring(post.read_perm) and player == author or player in post.comments.values_list('author', flat=True):
                player.msg(
                    "New comment on post {}/{} by |c{}|n.".format(board.id, post.id, author.name))

    def delete_post(self, post_id):
        "Delete a post."
        post = Post.objects.get(id=post_id)
        if not self.caller == post.author:
            self.caller.msg("You do not have permission to delete this post.")
            return
        post.delete()
        self.caller.msg("Deleted post {}.".format(post_id))

    def delete_comment(self, comment_id):
        "Delete a comment."
        comment = Comment.objects.get(id=comment_id)
        if not self.caller == comment.author:
            self.caller.msg(
                "You do not have permission to delete this comment.")
            return
        comment.delete()
        self.caller.msg("Deleted comment {}.".format(comment_id))

    def read_all_unread(self, group_name):
        # Code to mark all unread posts in a group as read
        # You would modify self.caller.db.read_posts here
        pass

    def mark_all_as_read(self, group_name):
        # Code to mark all posts in a group as read
        # You would modify self.caller.db.read_posts here
        pass

    def scan_for_unread(self):
        # Code to list the number of unread posts in each group
        # You would read from self.caller.db.read_posts here
        pass

    def split_post(self, args):
        # Code to post a message in multiple parts
        # This might not require modifying self.caller.db
        pass

    def leave_group(self, group_name):
        # Code to remove the player from a group
        # You would modify self.caller.db.groups here
        pass

    def join_group(self, group_name):
        # Code to add the player to a group
        # You would modify self.caller.db.groups here
        pass
def format_board_posts_output(self, posts, board):
    """
    Helper function to format board posts for display.
    """
    output = "|b=|n" * 78 + "\n"
    output += "|w**** {} ****|n".format(board.name).center(78)
    output += "\n" + "|b=|n" * 78 + "\n"
    output += "|wID|n".ljust(4)
    output += "  |wTitle|n".ljust(35)
    output += "      |wAuthor|n".ljust(22)
    output += "          |wDate Posted".ljust(13)
    output += "\n" + "|b=|n" * 78 + "\n"
    for post in posts:
        output += str(post.id).ljust(4)
        output += post.title.ljust(35)
        output += str(post.author.username).ljust(22)
        output += post.created_at.strftime("%Y-%m-%d")
        output += "\n" + "|b=|n" * 78
    return output
    
def format_post(self, post):
    """
    Helper function to format a single post for display.
    """
    output = "|b=|n" * 78 + "\n"
    output += "|wTitle: |n{}\n".format(post.title)
    output += "|wAuthor: |n{}\n".format(post.author.username)
    output += "|wDate: |n{}\n".format(post.created_at.strftime("%Y-%m-%d"))
    output += "|b=|n" * 78 + "\n"
    output += "{}\n".format(post.body)
    output += "|b=|n" * 78
    # Display comments if any
    comments = post.comments.all()
    if comments:
        output += "\n|wComments:|n\n"
        for comment in comments:
            output += "|w{}|n - {}: {}\n".format(
                comment.id,
                comment.author.username,
                comment.body
            )
    return output
