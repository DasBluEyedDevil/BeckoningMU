from evennia.utils.ansi import ANSIString


def target(context):
    key = context.lhs.lower()
    target = context.caller
    instance = ""
    value = context.rhs or ""
    specialty = ""

    # determine if we're setting a target and stat
    if "/" in key:
        target = context.caller.search(
            key.split("/")[0], global_search=True)
        key = key.split("/")[1]

        if not key:
            return

        # Split the key into the fixed key.
        key = context.lhs.split("/")[1]
        target = context.caller

    key = key.split("(")
    if len(key) > 1:
        instance = context.args.split("(")[1]
        instance = instance.split(")")[0]

    key = key[0]

    # split the value into the value and specialty
    if "/" in value:
        specialty = value.split("/")[1]
        value = value.split("/")[0]
    return {
        "target": target,
        "key": key,
        "value": value,
        "instance": instance,
        "specialty": specialty
    }


def is_approved(target):
    try:
        if target.db.stats["approved"] == True or target.perm_check("Admin"):
            return True
        else:
            return False
    except:
        return False


def is_ic(target):
    if target.db.stats["ic"] == True:
        return True
    else:
        return False


def format(key="", val=0, width=24, just="rjust", type="", temp=0):
    title = "|w" if val else "|x"
    title += key.capitalize() + ":|n"
    text_val = "|w" if val else "|x"
    text_val += str(val) + "|n"
    if temp:
        text_val += f"|w({temp})|n"
    if just == "ljust":
        if type == "specialty":
            return ANSIString(ANSIString(title).ljust(20) + ANSIString("{}".format(str(val)))).ljust(width)[0:width]
        else:
            return ANSIString(ANSIString(title).ljust(15) + ANSIString("{}".format(str(val)))).ljust(width)[0:width]
    else:
        if type == "specialty":
            return "  " + ANSIString(ANSIString(title).ljust(width - 2 - len(ANSIString("{}".format(text_val))), ANSIString("|x.|n")) + "{}".format(text_val))
        else:
            return ANSIString(ANSIString(title).ljust(width - len(ANSIString("{}".format(text_val))), ANSIString("|x.|n")) + "{}".format(text_val))
