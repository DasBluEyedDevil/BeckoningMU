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
    aliases = ["+BBS", "bbs", "+bb", "bb"]
    lock = "cmd:all()"
    help_category = "BBS"

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
        "This will be called when the command is issued."
        if not self.switches and not self.args:
            # If no switches or arguments are provided, list all accessible boards
            self.list_boards()
            return
        elif not self.switches and self.args:
            # If no switches are provided, but arguments are, view the specified board
            self.read_post(self.args)
            return

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
        else:
            self.caller.msg(
                "Invalid command. Type '+bbs/help' for usage instructions.")

    def list_boards(self):
        """
        List all boards that the caller has access to.
        """

        # ==============================================================================
        #       Group Name                     Last Post                 # of Messages
        # ==============================================================================
        # 1     General                         2019-01-01 12:00                     5
        # 2 (-) Announcements                   2019-01-01 12:00                    20
        # 3  *  Staff                           2019-01-01 12:00                     0
        # ==============================================================================
        # '*' = restricted     '-' = Read Only     '(-)' - Read Only, but you can write
        # ==============================================================================
        "List all boards."
        boards = Board.objects.all()
        output = ANSIString("|b=|n"*78) + "\n"
        output += ANSIString("      |wGroup Name|n").ljust(40)
        output += ANSIString("|wLast Post|n").ljust(24)
        output += ANSIString("|w# of Messages").ljust(15) + "\n"
        output += ANSIString("|b=|n"*78) + "\n"
        datetime_obj = None
        for board in boards:
            if board.read_perm == "all" or self.caller.check_permstring(board.read_perm):
                last_post = board.posts.last()
                if last_post:
                    print(last_post)
                    datetime_obj = datetime.fromisoformat(
                        str(last_post.created_at))

                if datetime_obj:

                    formatted_datetime = datetime_obj.strftime(
                        "%Y-%m-%d %H:%M:%S")
                else:
                    formatted_datetime = "None"

                last_post_date = formatted_datetime if last_post else "None"
                num_posts = board.posts.count()

                output += ANSIString(str(board.id))

                if board.read_perm.lower() not in ["all", "any", "public"]:
                    self.caller.msg(board.read_perm, board.write_perm)
                    output += ANSIString("  *  ").ljust(5)

                elif board.write_perm.lower() not in ["all", "any", "public"]:
                    if board.read_perm == "all" or self.caller.check_permstring(board.write_perm):
                        output += ANSIString(" (-) ").ljust(5)
                    else:
                        output += ANSIString("  -  ").ljust(5)
                else:
                    output += ANSIString("    ").ljust(5)

                output += ANSIString(board.name[:34]).ljust(35)
                output += ANSIString(str(last_post_date)).ljust(22)
                output += ANSIString(str(num_posts)).rjust(13) + "\n"

        output += ANSIString("|b=|n"*78) + "\n"
        output += "* = restricted     - = read only      (-) read only but you can write.\n"
        output += ANSIString("|b=|n"*78) + "\n"

        self.caller.msg(output)

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

    def view_board(self, board_name):
        "View all posts on a board."
        # ==============================================================================
        #                              **** Announcements ****
        #       Message                            Posted             By    
        # ------------------------------------------------------------------------------
        # 1     Welcome to the game!               2019-01-01 12:00   Admin          0
        # 1.1   `RE: Welcome to the game!`         2019-01-01 12:00   Admin          0
        # 2     New rules!                         2019-01-01 12:00   Admin          1
        # 3     Another TItle!                     2019-01-01 12:00   Admin         10
        # =============================================================================

        # if no board name is given, list all boards.
        if not board_name:
            self.list_boards()
            return
    
        try:
            board = Board.objects.get(name=board_name)
        except Board.DoesNotExist:
            self.caller.msg("No board by that name exists.")
            return
    
        # Assuming your permission system is based on the caller having specific
        # permissions stored in a field like `read_perm` on the board.
        if not self.caller.check_permstring(board.read_perm):
            self.caller.msg("You do not have permission to view this board.")
            return
    
        # Proceed with listing the posts on the board as before
        posts = board.posts.all()
        output = format_board_posts_output(posts, board)
        self.caller.msg(output)
    
        def format_board_posts_output(posts, board):
        output = ANSIString("|b=|n"*78) + "\n"
        output += ANSIString(f"**** |w{board.name}|n ****").center(78) + "\n"
        output += ANSIString("|wMessage|n").ljust(35)
        output += ANSIString("|wPosted|n").ljust(22)
        output += ANSIString("|wBy|n").ljust(13)
        output += ANSIString("|wComments|n").rjust(3) + "\n"
        output += ANSIString("|b-|n"*78) + "\n"

        for post in posts:
            output += ANSIString(str(post.id)).ljust(4)
            output += ANSIString(post.title[:30]).ljust(35)
            output += ANSIString(str(post.created_at.strftime("%Y-%m-%d %H:%M"))).ljust(22)
            output += ANSIString(str(post.author)[:10]).ljust(13)
            output += ANSIString(str(post.comments.count())).rjust(3) + "\n"    
            output += ANSIString("|b=|n"*78) + "\n"
        return output


    def read_post(self, args):
        # ==============================================================================
        # Title: Welcome to the game!               Board: Announcements (1/2)
        # Author: Admin                             Posted: 2019-01-01 12:00
        # Date: 2019-01-01 12:00                    Replies: 2 (Locked)
        # ------------------------------------------------------------------------------
        # Welcome to the game! This is a test post.
        # ==============================================================================
        "Read a post and its comments."
        try:
            board_id, post_id = args.split("/")
        except ValueError:
            board_id = args
            post_id = None

        if board_id:
            try:
                try:
                    board = Board.objects.get(id=board_id)
                except ValueError:
                    board = Board.objects.get(name=board_id)
            except Board.DoesNotExist:
                self.caller.msg("No board by that name or ID exists.")
                return
            if not self.caller.check_permstring(board.read_perm):
                self.caller.msg(
                    "You do not have permission to read this board.")
                return

            if post_id:
                try:
                    try:
                        post = board.posts.get(id=post_id)
                    except Post.DoesNotExist:
                        post = board.posts.get(title=post_id)
                # if the post doesn't exist, just view the board.
                except Post.DoesNotExist:
                    self.view_board(board_id)
                    return
            else:
                self.view_board(board_id)
                return

            if not self.caller.check_permstring(board.read_perm):
                self.caller.msg(
                    "You do not have permission to read this board.")
                return

        if not post:
            self.caller.msg("No post by that name or ID exists.")
            return
        if not self.caller.check_permstring(post.read_perm):
            self.caller.msg("You do not have permission to read this post.")
            return

        output = ANSIString("|b=|n"*78) + "\n"
        output += ANSIString("|wTitle:|n {}".format(post.title)).ljust(39)
        output += ANSIString("|wBoard:|n {} ({}/{})".format(board.name,
                             board_id, post_id)).ljust(39) + "\n"
        output += ANSIString("|wAuthor:|n {}".format(post.author)).ljust(39)
        output += ANSIString("|wPosted:|n {}".format(
            post.created_at.strftime("%Y-%m-%d %H:%M"))).ljust(39) + "\n"
        output += ANSIString("|wReplies:|n {}".format(
            post.comments.count())).ljust(39) + "\n"
        output += ANSIString("|b-|n"*78) + "\n"
        output += ANSIString(post.body) + "\n"

        comments = post.comments.all()

        if comments:
            output += ANSIString("|b-|n"*78) + "\n"
            output += ANSIString("|wReplies:|n") + "\n"
            output += ANSIString("|b-|n"*78) + "\n"
            for comment in comments:
                com = ANSIString("|w{}. {} - {}|n".format(
                    comment.id, comment.created_at.strftime("%Y-%m-%d %H:%M"), comment.author.name)) + ": "
                com += ANSIString(comment.body) + "\n"
                output += com[:78]
        else:
            output += ANSIString("|b-|n"*78) + "\n"
            output += ANSIString("|wNo Replies.|n") + "\n"
        output += "%r" + ANSIString("|b=|n"*78) + "\n"
        self.caller.msg(output)

    from evennia.accounts.models import AccountDB  # Adjust the import path as necessary

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
        "Comment on a post."

        # first we need to break the post_id into board_id and post_id
        board_id, post_id = post_id.split("/")
        try:
            board = Board.objects.get(id=board_id)
        except ValueError:
            board = Board.objects.get(name=board_id)
        except Board.DoesNotExist:
            self.caller.msg("No board by that name or ID exists.")
            return

        try:
            post = board.posts.get(id=post_id)
        except Post.DoesNotExist:
            self.caller.msg("No post by that name or ID exists.")
            return

        if not self.caller.check_permstring(post.read_perm):
            self.caller.msg("You do not have permission to read this post.")
            return
        author = AccountDB.objects.get(id=self.caller.id)
        Comment.objects.create(
            author=author, post=post, body=comment_body)

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


class classCmdBbRead(MuxCommand):
    """
    Read a board, or post from the bbs.  A shortcut for +bb.

    Usage:
      +bbread <board name or ID>
      +bbread <board name or ID>/<post name or ID>

    """

    key = "+bbread"
    aliases = ["bbread"]
    locks = "cmd:all()"
    help_category = "BBS"

    def func(self):
        "Implement the command."
        comment = None
        try:
            board_name, post_name = self.args.split("/")
        except ValueError:
            board_name = self.args
            post_name = None

        if post_name:
            try:
                post, comment = post_name.split(".")
            except ValueError:
                post = post_name

        # call CmdBBS.read_post.
        if comment:
            self.caller.execute_cmd(
                "bb {}/{}.{}".format(board_name, post, comment))
        elif post_name:
            self.caller.execute_cmd("bb {}/{}".format(board_name, post))
        else:
            self.caller.execute_cmd("bb {}".format(board_name))
