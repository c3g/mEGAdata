import globals

# Print response
# Is this still used?
def print_response(r):
    print_response_status_code(r)
    # print(r.headers)
    print(r.text)

# Is this still used?
def print_response_status_code(r):
    print(r.status_code)

# Write config file to disk.
def write_config():
    with open("settings.ini", "w") as configfile:
        globals.config.write(configfile)

# Add an integer increment to the EGA Object alias to ensure uniqueness. 
def alias_increment(alias):
    if globals.config.getboolean("global", "alias_increment"):
        return alias + "_" + globals.config["global"]["alias_append"]
    else:
        return alias

# Strip the alias of any autoincrement.  Used for lookup in the obj_registries.
def alias_raw(alias):
    if globals.config.getboolean("global", "alias_increment"):
        return alias.replace("_" + globals.config["global"]["alias_append"], "")
    else:
        return alias
