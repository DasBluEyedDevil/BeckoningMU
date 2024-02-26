"""
File-based help entries. These complements command-based help and help entries
added in the database using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'text': <str>}``     # the actual help text. Can contain # subtopic sections
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'locks': <str>       # optional, 'view' controls seeing in help index, 'read'
                          #           if the entry can be read. If 'view' is unset,
                          #           'read' is used for the index. If unset, everyone
                          #           can read/view the entry.

"""

HELP_ENTRY_DICTS = [
    {
        "key": "evennia",
        "aliases": ["ev"],
        "category": "General",
        "locks": "read:perm(Developer)",
        "text": """
            Evennia is a MU-game server and framework written in Python. You can read more
            on https://www.evennia.com.

            # subtopics

            ## Installation

            You'll find installation instructions on https://www.evennia.com.

            ## Community

            There are many ways to get help and communicate with other devs!

            ### Discussions

            The Discussions forum is found at https://github.com/evennia/evennia/discussions.

            ### Discord

            There is also a discord channel for chatting - connect using the
            following link: https://discord.gg/AJJpcRUhtF

        """,
    },
    {
        "key": "building",
        "category": "building",
        "text": """
            Evennia comes with a bunch of default building commands. You can
            find a beginner tutorial in the Evennia documentation.

        """,
    },
    {
        key = "+bbs"
        aliases = ["+BBS", "bbs", "+bb", "bb", "bbview", "bbread"]
        lock = "cmd:all()"
        help_category = "BBS"
        "text": """
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
        
            Updated bbread functionality.
        
            Usage:
              bbread             - List all boards
              bbread <board_id>  - View board by id
              bbread <board_name>- View board by name
              bbread <board_id>/<post_id>   - Read post by board id and post id
              bbread <board_name>/<post_id> - Read post by board name and post id
              bbread <board_name>/<post_name> - Read post by board name and post name
            """
    },
]
