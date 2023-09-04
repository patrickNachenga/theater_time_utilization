# -------------------------  Version 3 -------------------------
# -------------------------  Version 3 -------------------------

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
            'enrolments[0][roleid]': self.get_role_id_by_short_name(role_name),
            'enrolments[0][userid]': user_id,
            'enrolments[0][courseid]': course_id
        }

        print(data)



        response = self.sendRequest(data)
        print(response.json())
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

        serverUrl = settings.MOODLE_SITE_URL + '/webservice/rest/server.php' + '?wstoken=' + settings.MOODLE_TOKEN + '&wsfunction=' + functionname + '&moodlewsrestformat=json'
        response = self.sendRequest(param, serverUrl)
        if response is False:
            return False

        responseData = response.json()
        # print(responseData)
        if 'loginurl' in responseData:
            loginurl = responseData['loginurl']
        else:
            return False

        path = ''
        if course_id is not None:
            path = "&wantsurl=" + settings.MOODLE_SITE_DOMAIN + '/course/view.php?id=' + str(course_id)

        # if 'modname' in locals() and 'activityid' in locals():
        #     path = self.SITE_DOMAIN + "/mod/" + str(modname) + "/view.php?id=" + str(activityid)

        full_path = loginurl + path
        # print(full_path)
        return full_path

    @staticmethod
    def grading_method():
        grading_methods_data = [
            {"id": 1, "name": "First attempt"},
            {"id": 2, "name": "Average grade"},
            {"id": 3, "name": "Last attempt"}
        ]
        return grading_methods_data

    @staticmethod
    def grade_filter(data, filter_type):
        last_sum_grades = 0
        last_sum_grades_user_id = None

        first_sum_grades = None
        first_sum_grades_user_id = None

        sum_grades_total = 0
        num_attempts = len(data)

        for index, quiz_attempt in enumerate(data):
            if quiz_attempt['sumgrades'] > last_sum_grades:
                last_sum_grades = quiz_attempt['sumgrades']
                last_sum_grades_user_id = quiz_attempt['userid']

            if first_sum_grades is None:
                first_sum_grades = quiz_attempt['sumgrades']
                first_sum_grades_user_id = quiz_attempt['userid']

            sum_grades_total += quiz_attempt['sumgrades']

        average_sum_grades = sum_grades_total / num_attempts if num_attempts > 0 else 0

        if filter_type == 1:
            return {
                'userid': first_sum_grades_user_id,
                'grades': first_sum_grades
            }
        elif filter_type == 2:
            return {
                'userid': first_sum_grades_user_id,
                'grades': average_sum_grades
            }

    def get_quizzes_by_course(self, course_id):
        data = {
            'wstoken': settings.MOODLE_TOKEN,
            'wsfunction': 'mod_quiz_get_quizzes_by_courses',
            'moodlewsrestformat': 'json',
            'courseids[0]': course_id
        }

        response = self.sendRequest(data)

        if response is False:
            # Handle the error condition
            # print('Failed to get quizzes for the course.')
            return False

        response_data = response.json()

        if 'exception' in response_data:
            # Handle the API error condition
            # print('API Error: ' + response_data['message'])
            return False
        else:
            if response_data:
                # Check if the response contains the quizzes
                if 'quizzes' in response_data and isinstance(response_data['quizzes'], list):
                    return response_data['quizzes']  # Return the quizzes
                else:
                    # print('No quizzes found for the course.')
                    return False
            else:
                # print('Empty response received.')
                return False

    def get_user_attempts_on_quiz(self, quiz_id, grading_method, user_id):
        data = {
            'wstoken': settings.MOODLE_TOKEN ,
            'wsfunction': 'mod_quiz_get_user_attempts',
            'moodlewsrestformat': 'json',
            'userid': user_id,
            'quizid': quiz_id
        }
        response = self.sendRequest(data)
        if response is False:
            # Handle the error condition
            # print('Failed to get user attempts on the quiz.')
            return False

        responseData = response.json()
        if 'exception' in responseData:
            # Handle the API error condition
            # print('API Error: ' + responseData['message'])
            return False
        else:
            if responseData:
                if 'attempts' in responseData and isinstance(responseData['attempts'], list):
                    if responseData['attempts']:
                        return self.grade_filter(responseData['attempts'], grading_method)  # Return the attempts
                    else:
                        return False
                else:
                    # print('No attempts found for the user on the quiz.')
                    return False
            else:
                # print('Empty response received.')
                return False

    def get_users_attempts_on_quiz(self, quiz_id, grading_method, user_id_array):
        result = []
        for value in user_id_array:
            current_res = self.get_user_attempts_on_quiz(quiz_id, grading_method, value)
            if current_res:
                result.append(current_res)
        return result

# moodle_api = MoodleApi()
# login_url = moodle_api.getloginurl("admin")
# print(login_url)
