"""
  Copyright 2019 Eugene Byeong Kyun Kim.

  This file is subject to the terms and conditions defined in
  file 'LICENSE', which is part of this source code package.
"""

import requests
import json


class TeamCityRestApiClientWrapper(object):
    """
    Module wrapping TeamCity REST API.
    Visit JetBrains website for TeamCity REST API details: https://www.jetbrains.com/help/teamcity/rest-api.html
    """

    # region Construction

    def __init__(self, server, port, username, password):
        """ Construction
        :param username: login ID to the server.
        :param password: Password of the user.
        :param server: IP address or http url of the TeamCity server.
        :param port: Port of the TeamCity server,
        """
        self.server = server
        self.port = port
        self.username = username
        self.password = password
        self.baseUrl = "http://%s:%d/httpAuth/app/rest" % (self.server, self.port)
        self.auth = (self.username, self.password)
        self.session = requests.Session()

    # endregion

    # region Public methods

    def create_new_blank_project(self, name, project_id, parent_project_id) -> None:
        """ Create a new blank project.
        :param name: Name of the new project.
        :param project_id: ID of the new project. Ensure to ID is unique.
        :param parent_project_id: ID of the parent project. The new project will be created under this parent project.
        :return: None
        """
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
        data = '<newProjectDescription name="' + name + '" id="' + project_id + '">\n' + \
               '<parentProject locator="id:' + parent_project_id + '"/>\n' + \
               '</newProjectDescription>'

        self.send_request("POST", "projects", headers=headers, data=data)

    def copy_build_type(self, new_build_type_name, destination_project_id, source_build_type_id) -> None:
        """
        :param new_build_type_name: name of the build configuration will be newly created.
        :param destination_project_id: ID of the project where the new build type will be located.
        :param source_build_type_id: existing build type will be copied from.
        :return: None
        """
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
        data = '<newBuildTypeDescription name="' + new_build_type_name + '" ' +\
               'sourceBuildTypeLocator="id:' + source_build_type_id + '" ' +\
               'copyAllAssociatedSettings="true" shareVCSRoots="false"/>'

        self.send_request("POST", "projects/id:" + destination_project_id + "/buildTypes", headers=headers, data=data)

    def attach_template_to_build_type(self, template_id, build_type_id) -> None:
        """ Attach a template to the build type. This can be used to replace the template which is already attached to
        the build type with the template.
        :param template_id: ID of the build type template to use
        :param build_type_id: ID of the build type where the template is attached to.
        :return: None
        """
        headers = {'Content-Type': 'text/plain', 'Accept': 'application/json'}
        self.send_request("PUT", "buildTypes/" + build_type_id + "/template", headers=headers, data=template_id)

    def detach_template_from_build_type(self, build_type_id) -> None:
        """ Detach the template from the build type.
        :param build_type_id: ID of the build type where the template is detached from.
        :return: None
        """
        self.send_request("DELETE", "buildTypes/" + build_type_id + "/template")

    def create_build_type(self, new_build_type_name, destination_project_id) -> str:
        """ Create a new build type.
        :param new_build_type_name: name of the new build type
        :param destination_project_id: ID of the project where the new build type will be located.
        :return: ID of the build type newly created.
        """
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
        data = '<newBuildTypeDescription name="' + new_build_type_name + '" ' + \
               'copyAllAssociatedSettings="true" shareVCSRoots="false"/>'

        response = self.send_request("POST",
                                     "projects/id:" + destination_project_id + "/buildTypes",
                                     headers=headers,
                                     data=data)
        return response["id"]

    def run_build_type(self, build_type_id) -> None:
        """ Run the build type.
        :param build_type_id: ID of the build type.
        :return: None
        """
        headers = {'Content-Type': 'application/xml', 'Accept': 'application/json'}
        data = '<build><buildType id="' + build_type_id + '"/></build>'

        self.send_request("POST", "buildQueue", headers=headers, data=data)

    def get_projects(self) -> dict:
        """ Get a list of projects.
        :return: List of projects as the dictionary format.
        """
        return self.get("projects")

    def get_build_types(self) -> dict:
        """ Get a list of build types.
        :return: List of build types as the dictionary format.
        """
        return self.get("buildTypes")

    def get_build_type(self, build_type_id) -> dict:
        """ Get details of a build type.
        :param build_type_id: ID of the build type.
        :return: Details of the build type as the dictionary format.
        """
        return self.get("buildTypes/" + build_type_id)

    def get_build_type_parameters(self, build_type_id) -> dict:
        """ Get parameters of the build type.
        :param build_type_id: ID if the build type.
        :return: List of parameters of the build type as dictionary format.
        """
        return self.get("buildTypes/" + build_type_id + "/parameters")

    def update_build_type_parameters(self, build_type_id, user_params) -> None:
        """ Update values of parameters
        :param build_type_id: ID of the build type where the parameters exist.
        :param user_params: Dictionary with parameters and their new values.
        :return: Update values of parameters of the build type.
        """
        # Ensure the parameters from user exist in the server.

        server_params = self.get_build_type_parameters(build_type_id)
        invalid_parameters = set([p for p in user_params.keys()]) - set([p["name"] for p in server_params["property"]])

        if len(invalid_parameters) > 0:
            raise ValueError("Ensure the parameters exist in the server: " + '.'.join(invalid_parameters))

        # Update values of server parameters.

        for k, v in user_params.items():
            for p in server_params["property"]:
                if p["name"] == k:
                    p["value"] = v

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

        self.send_request("PUT",
                          "buildTypes/" + build_type_id + "/parameters",
                          headers=headers,
                          data=json.dumps(server_params))

    # endregion

    # region Private methods

    def get(self, api):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        return self.send_request('GET', api, headers=headers)

    def send_request(self, method, url, **kwargs):
        headers = kwargs.get("headers")
        data = kwargs.get("data")
        full_url = self.get_url(url)

        prepared = requests.Request(method, full_url, auth=self.get_auth(), headers=headers, data=data).prepare()
        response = self.session.send(prepared)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)

        # Status code
        # 204 - Succeeded. no content.
        if response.status_code == 204:
            return

        if response.headers['Content-Type'] == 'application/json':
            return response.json()
        else:
            return response.content

    def get_url(self, url):
        return '/'.join((self.baseUrl, url))

    def get_auth(self):
        return self.username, self.password

    # endregion
