from TeamCityRestApiClient import TeamCityRestApiClientWrapper

# Provide your own configurations.
server = "127.0.0.1"
port = 80
username = "admin"
password = "admin"

# Create the instance of the wrapper.
tc = TeamCityRestApiClientWrapper(server, port, username, password)


def show_build_types():
    # Show build types.
    build_types = tc.get_build_types()

    # Total number of build types.
    print("Number of build types: {}".format(build_types["count"]))

    # Show the name and ID of the build type.
    for build_type in build_types["buildType"]:
        print(" - [{}] {} (ID: {})".format(build_types["buildType"].index(build_type) + 1,
                                           build_type["name"],
                                           build_type["id"]))


def show_build_types_using_template():
    # Get build types which use the particular template.
    template_id = "Games_Template"
    build_types = tc.get_build_types()
    build_types_using_template = []

    for build_type in build_types["buildType"]:

        # Get details of the build type.
        build_type_details = tc.get_build_type(build_type["id"])

        templates = build_type_details["templates"]

        # Add the build type if it uses the template.
        if int(templates["count"]) > 0:
            for template in templates["buildType"]:
                if template["id"] == template_id:
                    build_types_using_template.append(build_type)
                    continue

    # Show the name and ID of the build type.

    if len(build_types_using_template) > 0:
        for build_type in build_types_using_template:
            print(" - [{}] {} (ID: {})".format(build_types_using_template.index(build_type) + 1,
                                               build_type["name"],
                                               build_type["id"]))
    else:
        print("No build types using the template ({}) found.".format(template_id))


def show_build_type_parameters():
    # Show all parameters of the build type.
    build_type_id = "Games_MyFlashCardsGame"

    parameters = tc.get_build_type_parameters(build_type_id)

    # Total number of parameters.
    print("Parameters for {}".format(build_type_id))
    print("Number of parameters: {}".format(parameters["count"]))

    # Show the name and ID of the build type.
    for prop in parameters["property"]:
        print(" - {}: {}".format(prop["name"], prop["value"]))


def create_build_type():
    # Create a new build type.

    destination_project_id = "Projects_Games"
    template_id = "Games_Template"
    new_build_type_name = "My Flash Card Game2"
    parameters = {
        "p4.depot": "//Games/MyFlashCardGame2/Trunk",
        "game.platform": "Android",
        "game.version": "1.0.2044"
    }

    # Check if the build_type_name is already being used.

    build_types = tc.get_build_types()

    for build_type in build_types["buildType"]:

        # TeamCity automatically gives a new name if it is already being used.
        # But we here demonstrate the name is unique within a project.

        if build_type["projectId"] == destination_project_id and \
                build_type["name"].lower() == new_build_type_name.lower():
            print("the build type name ({}) is already being used. Use different name.".format(new_build_type_name))
            pass

    # Create a new blank build type.
    new_build_type_id = tc.create_build_type(new_build_type_name, destination_project_id)

    # Attach the template to the build type.
    tc.attach_template_to_build_type(template_id, new_build_type_id)

    # Update values of some parameters from the template as they are presumably just place-holders for the build type.
    tc.update_build_type_parameters(new_build_type_id, parameters)


# Test methods calls.

#show_build_types()
#show_build_types_using_template()
#show_build_type_parameters()
#create_build_type()