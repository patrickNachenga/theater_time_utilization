import requests

from src.core.config import settings


class MoodleApi:

    def sendRequest(self, data, url=None):
        if url is None:
            url = settings.MOODLE_SITE_URL
        response = requests.post(url, data=data)
        return response

    def createFalcuty(self, shortname, fullname, description):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_create_categories',
            'moodlewsrestformat': 'json',
            'categories[0][name]': fullname,
            'categories[0][description]': description,
            'categories[0][idnumber]': shortname,
        }

        response = self.sendRequest(data)

        responseData = response.json()

        if 'exception' in responseData:
            # print(responseData)
            return 0
        else:
            if responseData:
                if 'id' in responseData[0]:
                    return responseData[0]['id']
                elif 'warnings' in responseData and responseData['warnings'][0]['itemid']:
                    return responseData['warnings'][0]['itemid']
                else:
                    return 0
            else:
                return 0

    def updateFaculty(self, facultyId, shortname, fullname, description):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_update_categories',
            'moodlewsrestformat': 'json',
            'categories[0][id]': facultyId,
            'categories[0][name]': fullname,
            'categories[0][description]': description,
            'categories[0][idnumber]': shortname
        }

        response = self.sendRequest(data)

        responseData = response.json()

        if 'exception' in responseData:
            return False
        else:
            return True

    def createDepartment(self, facultyId, departmentName, departmentDescription):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_create_categories',
            'moodlewsrestformat': 'json',
            'categories[0][name]': departmentName,
            'categories[0][description]': departmentDescription,
            'categories[0][parent]': facultyId
        }

        response = self.sendRequest(data)

        responseData = response.json()

        if 'exception' in responseData:
            # print('API Error:', responseData['message'])
            return 0
        else:
            if responseData:
                if 'id' in responseData[0]:
                    return responseData[0]['id']
                else:
                    return 0
            else:
                return 0

    def updateDepartment(self, departmentId, newName, newDescription):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_update_categories',
            'moodlewsrestformat': 'json',
            'categories[0][id]': departmentId,
            'categories[0][name]': newName,
            'categories[0][description]': newDescription
        }

        response = self.sendRequest(data)

        responseData = response.json()

        if 'exception' in responseData:
            return False
        else:
            return True

    def get_role_id_by_short_name(self, role_short_name):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'moodlewsrestformat': 'json',
            'wsfunction': 'local_wsgetroles_get_roles',
            'shortnames[0]': role_short_name,
        }
        response = self.sendRequest(data)
        response_data = response.json()

        if 'exception' in response_data:
            # Handle the API error condition
            print('API Error:', response_data['message'])
            return False
        else:
            if response_data:
                for role in response_data:
                    if role['shortname'] == role_short_name:
                        return role['id']
                # Role not found
                return False
            else:
                # Empty response received
                return False

    def createCustomCategory(self, parentId, categoryName, categoryDescription):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_create_categories',
            'moodlewsrestformat': 'json',
            'categories[0][name]': categoryName,
            'categories[0][description]': categoryDescription,
            'categories[0][parent]': parentId
        }

        response = self.sendRequest(data)

        if response is False:
            # print('cURL Error: Failed to send the request.')
            return 0

        responseData = response.json()

        if 'exception' in responseData:
            # print('API Error:', responseData['message'])
            return 0
        else:
            if responseData:
                if 'id' in responseData[0]:
                    print(responseData[0]['id'])
                    return responseData[0]['id']
                else:
                    # print('Unable to retrieve the department ID.')
                    return 0
            else:
                # print('Empty response received.')
                return 0

    def updateCustomCategory(self, categoryId, newName, newDescription):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_update_categories',
            'moodlewsrestformat': 'json',
            'categories[0][id]': categoryId,
            'categories[0][name]': newName,
            'categories[0][description]': newDescription
        }

        response = self.sendRequest(data)

        if response is False:
            # print('cURL Error: Failed to send the request.')
            return False

        responseData = response.json()

        if 'exception' in responseData:
            # print('API Error:', responseData['message'])
            return False
        else:
            if responseData:
                if 'id' in responseData[0]:
                    return responseData[0]['id']
                else:
                    # print('Unable to retrieve the updated category ID.')
                    return False
            else:
                # print('Empty response received.')
                return False

    # def deleteCustomCategory(self, categoryId):
    #     data = {
    #         'wstoken': self.TOKEN,
    #         'wsfunction': 'core_course_delete_categories',
    #         'moodlewsrestformat': 'json',
    #         'categoryids[0]': categoryId,
    #         'recursive': 1
    #     }

    #     response = self.sendRequest(data)

    #     # print(response.text)
    #     # exit()

    #     if response is False:
    #         # print('cURL Error: Failed to send the request.')
    #         return False

    #     responseData = response.json()

    #     if 'exception' in responseData:
    #         # print('API Error:', responseData['message'])
    #         return False
    #     else:
    #         if responseData:
    #             if 'id' in responseData[0]:
    #                 return responseData[0]['id']
    #             else:
    #                 # print('Unable to retrieve the deleted category ID.')
    #                 return False
    #         else:
    #             # print('Empty response received.')
    #             return False

    def createCourse(self, departmentId, courseFullName, courseShortName, courseDescription):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_create_courses',
            'moodlewsrestformat': 'json',
            'courses[0][fullname]': courseFullName,
            'courses[0][shortname]': courseShortName,
            'courses[0][categoryid]': departmentId,
            'courses[0][summary]': courseDescription
        }

        response = self.sendRequest(data)

        if response is False:
            print('cURL Error: Failed to send the request.')
            return 0

        responseData = response.json()

        if 'exception' in responseData:
            print('API Error:', responseData['message'])
            return 0
        else:
            if responseData:
                if 'id' in responseData[0]:
                    return responseData[0]['id']
                else:
                    print('Unable to retrieve the course ID.')
                    return 0
            else:
                print('Empty response received.')
                return 0

    def create_group(self, course_id, group_name, group_description):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_group_create_groups',
            'moodlewsrestformat': 'json',
            'groups[0][courseid]': course_id,
            'groups[0][name]': group_name,
            'groups[0][description]': group_description,
            'groups[0][visibility]': 1
        }

        response = self.sendRequest(data)

        if response is False:
            # Handle the error condition
            print('Failed to create group.')
            return False

        response_data = response.json()

        if 'exception' in response_data:
            # Handle the API error condition
            print('API Error:', response_data['message'])
            return False
        else:
            if response_data:
                # Check if the response contains the group ID
                if 'id' in response_data[0]:
                    return response_data[0]['id']
                else:
                    print('Unable to retrieve the group ID.')
                    return False
            else:
                print('Empty response received.')
                return False

    def add_member_to_group(self, group_id, user_id):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_group_add_group_members',
            'moodlewsrestformat': 'json',
            'members[0][groupid]': group_id,
            'members[0][userid]': user_id
        }

        response = self.sendRequest(data)

        if response is False:
            # Handle the error condition
            print('cURL Error: Failed to send the request.')
            return False
        if response.status_code == 200:
            return True
        response_data = response.json()

        if 'exception' in response_data:
            # Handle the API error condition
            print('API Error:', response_data['message'])
            return False
        else:
            return True

    def enroll_user_as_user(self, user_id, course_id, role_name):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'enrol_manual_enrol_users',
            'moodlewsrestformat': 'json',
            'enrolments[0][roleid]':  self.get_role_id_by_short_name(role_name),
            'enrolments[0][userid]': user_id,
            'enrolments[0][courseid]': course_id
        }

        response = self.sendRequest(data)
        if response is False:
            # Handle the error condition
            print('Failed to enroll user.')
            return False

        if response.status_code == 200:
            return True
        response_data = response.json()
        if 'exception' in response_data:
            # Handle the API error condition
            print('API Error:', response_data['message'])
            return False
        else:
            return True

    def updateCourse(self, courseId, newFullName, newShortName, newDescription):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_update_courses',
            'moodlewsrestformat': 'json',
            'courses[0][id]': courseId,
            'courses[0][fullname]': newFullName,
            'courses[0][shortname]': newShortName,
            'courses[0][summary]': newDescription
        }

        response = self.sendRequest(data)

        if response is False:
            # print('cURL Error: Failed to send the request.')
            return False

        responseData = response.json()

        if 'exception' in responseData:
            # print('API Error: ' + responseData['message'])
            return False
        else:
            if responseData:
                if 'id' in responseData[0]:
                    return responseData[0]['id']
                else:
                    # print('Unable to retrieve the updated course ID.')
                    return False
            else:
                # print('Empty response received.')
                return False

    def deleteCourse(self, courseId):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_course_delete_courses',
            'moodlewsrestformat': 'json',
            'courseids[0]': courseId
        }

        response = self.sendRequest(data)

        if response is False:
            # print('cURL Error: Failed to send the request.')
            return False

        responseData = response.json()

        if 'exception' in responseData:
            # print('API Error: ' + responseData['message'])
            return False
        else:
            if responseData:
                if 'id' in responseData[0]:
                    return responseData[0]['id']
                else:
                    # print('Unable to retrieve the deleted course ID.')
                    return False
            else:
                # print('Empty response received.')
                return False

    def createUser(self, username, password, firstname, lastname, email):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'core_user_create_users',
            'moodlewsrestformat': 'json',
            'users[0][username]': username,
            'users[0][password]': password,
            'users[0][firstname]': firstname,
            'users[0][lastname]': lastname,
            'users[0][email]': email,
        }

        response = self.sendRequest(data)
        # print(response.text)
        # exit()

        if response is False:
            # print('cURL Error: Failed to send the request.')
            return 0

        responseData = response.json()

        if 'exception' in responseData:
            # print('API Error: ' + responseData['message'])
            return 0
        else:
            if responseData:
                if 'id' in responseData[0]:
                    # print('User created with ID: ' + responseData[0]['id'])
                    return responseData[0]['id']
                else:
                    # print('Unable to retrieve the user ID.')
                    return 0
            else:
                # print('Empty response received.')
                return 0

    def getloginurl(self, username, course_id=None):
        functionname = 'auth_userkey_request_login_url'

        param = {
            'user[username]': username
        }

        serverUrl = settings.SITE_DOMAIN + '/webservice/rest/server.php' + '?wstoken=' + settings.MOODLE_TOKEN + '&wsfunction=' + functionname + '&moodlewsrestformat=json'
        response = self.sendRequest(param, serverUrl)
        if response is False:
            return False

        responseData = response.json()
        print(responseData)
        if 'loginurl' in responseData:
            loginurl = responseData['loginurl']
        else:
            return False

        path = ''
        if course_id is not None:
            path = "&wantsurl="+settings.SITE_DOMAIN + '/course/view.php?id=' + str(course_id)

        # if 'modname' in locals() and 'activityid' in locals():
        #     path = self.SITE_DOMAIN + "/mod/" + str(modname) + "/view.php?id=" + str(activityid)

        full_path =  loginurl + path
        print(full_path)
        return full_path

# moodle_api = MoodleApi()
# login_url = moodle_api.getloginurl("admin")
# print(login_url)
