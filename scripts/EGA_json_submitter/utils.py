import globals

# Print response
def print_response(r):
    print_response_status_code(r)
    # print(r.headers)
    print(r.text)

def print_response_status_code(r):
    print(r.status_code)

# Add a reason for this 
def alias_testing(alias):
    if globals.config["global"]["test_or_prod"] == "prod":
        return alias
    else:
        return alias + "_" + globals.config["session"]["alias_increment"]

# Add a reason for this function
def alias_raw(alias):
    if globals.config["global"]["test_or_prod"] == "prod":
        return alias
    else:
        return alias.replace("_" + globals.config["session"]["alias_increment"], "")
