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
        output += "  |wBoard Name|n".ljust(29)  # Adjusted spacing for new column
        output += " |wGroup|n".ljust(10)  # New column for read permissions
        output += "         |wLast Post|n".ljust(22)
        output += "           |w# of Messages".ljust(13) + "\n"
        output += "|b=|n" * 78 + "\n"
        for board in boards:
            if board.read_perm == "all" or self.caller.check_permstring(board.read_perm):
                last_post = board.posts.last()
                formatted_datetime = "None"
                if last_post:
                    formatted_datetime = last_post.created_at.strftime("%Y-%m-%d")
                num_posts = board.posts.count()
                read_perm_display = board.read_perm if board.read_perm != "all" else "-"
                output += "  " + board.name[:24].ljust(23)  # Adjusted spacing for new column
                output += read_perm_display.ljust(16)  # Display read permission
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
    
    def read_post(self, board, post_arg):
        "Read specific post."
        try:
            # Attempt to interpret post_arg as a sequence number first
            sequence_number = int(post_arg)  # Convert post_arg to an integer
            post = board.posts.get(sequence_number=sequence_number)
        except (ValueError, Post.DoesNotExist):
            # If conversion to int fails or no post with such sequence_number, try title
            try:
                post = board.posts.get(title__iexact=post_arg)
            except Post.DoesNotExist:
                self.caller.msg("Post not found by sequence number or title.")
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
    
        # Handle different commands
        if "boards" in self.switches:
            self.list_boards()
        elif "view" in self.switches:
            self.view_board(board_arg)
        elif "read" in self.switches:
            self.read_post(board_arg, post_arg)
        elif "post" in self.switches:
            board_name, post_content = self.args.split("=")
            post_title, post_body = post_content.split("/")
            self.post(board_name.strip(), post_title.strip(), post_body.strip())
        elif "comment" in self.switches:
            post_id, comment_body = self.args.split("=")
            self.comment(post_id.strip(), comment_body.strip())
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
    
            self.create_board(board_name.strip(), read_perm.strip(), write_perm.strip())
        elif "editboard" in self.switches:
            board_name, perms = self.args.split("=")
            read_perm, write_perm = perms.split("/")
            self.edit_board(board_name.strip(), read_perm.strip(), write_perm.strip())
        elif "deleteboard" in self.switches:
            self.delete_board(self.args)
        else:
            # No switches or unrecognized switch - List all boards or view board
            if not board_arg:
                self.list_boards()
            else:
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

    def comment(self, board_name_and_post_sequence, comment_body):
        """
        Comment on a post using the board name and post sequence number.
        """
        # Split the input into board_name and post_sequence
        try:
            board_name, post_sequence = board_name_and_post_sequence.split("/")
        except ValueError:
            self.caller.msg("Usage: comment <board_name>/<post_sequence> = <comment_body>")
            return
        
        # Attempt to find the board by name
        try:
            board = Board.objects.get(name__iexact=board_name)
        except Board.DoesNotExist:
            self.caller.msg("Board not found.")
            return
        
        # Attempt to find the post by sequence number within the board
        try:
            post = board.posts.get(sequence_number=post_sequence)
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
        
        # Notify all connected players who have either posted the post or commented on it.
        for player in AccountDB.objects.get_connected_accounts():
            if player.check_permstring(post.read_perm) and (player == author or player in post.comments.values_list('author', flat=True)):
                player.msg("New comment on post {}/{} by |c{}|n.".format(board.name, post.sequence_number, author.username))


    def delete_post(self, identifier):
        """
        Delete a post using board name and post sequence number.
        """
        try:
            board_name, post_sequence = identifier.split("/")
            board = Board.objects.get(name__iexact=board_name)
            post = board.posts.get(sequence_number=post_sequence)
        except (ValueError, Board.DoesNotExist, Post.DoesNotExist):
            self.caller.msg("Usage: delete_post <board_name>/<post_sequence>")
            return
    
        if not self.caller == post.author:
            self.caller.msg("You do not have permission to delete this post.")
            return
    
        post.delete()
        self.caller.msg(f"Deleted post {post_sequence} from board '{board_name}'.")


    def delete_comment(self, post_identifier, comment_id):
        """
        Delete a comment from a post, specified by board name and post sequence number.
        """
        try:
            board_name, post_sequence = post_identifier.split("/")
            board = Board.objects.get(name__iexact=board_name)
            post = board.posts.get(sequence_number=post_sequence)
            comment = post.comments.get(id=comment_id)  # Assuming comment ID is still used for direct identification
        except (ValueError, Board.DoesNotExist, Post.DoesNotExist, Comment.DoesNotExist):
            self.caller.msg("Usage: delete_comment <board_name>/<post_sequence> <comment_id>")
            return
    
        if not self.caller == comment.author:
            self.caller.msg("You do not have permission to delete this comment.")
            return
    
        comment.delete()
        self.caller.msg(f"Deleted comment {comment_id} from post '{post_sequence}' on board '{board_name}'.")


def format_board_posts_output(self, posts, board):
    """
    Helper function to format board posts for display, using sequence_number.
    """
    output = "|b=|n" * 78 + "\n"
    output += "|w**** {} ****|n".format(board.name).center(78) + "\n"
    output += "|b=|n" * 78 + "\n"
    output += "|wID|n".ljust(4)  # Changed from ID to Seq for sequence number
    output += "  |wTitle|n".ljust(35)
    output += "      |wAuthor|n".ljust(22)
    output += "             |wDate Posted".ljust(13) + "\n"
    output += "|b=|n" * 78 + "\n"
    for post in posts.order_by('sequence_number'):  # Ensure posts are ordered by sequence_number
        output += str(post.sequence_number).ljust(4)  # Use sequence_number
        output += post.title.ljust(35)
        output += str(post.author.username).ljust(22)
        output += "   " + post.created_at.strftime("%Y-%m-%d")
        output += "\n" + "|b=|n" * 78 + "\n"
    return output
    
def format_post(self, post):
    """
    Helper function to format a single post for display.
    """
    output = "|b=|n" * 78 + "\n"
    output += "|wPost Details|n".center(78) + "\n"
    output += "|b=|n" * 78 + "\n"
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

