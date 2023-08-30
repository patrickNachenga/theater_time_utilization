# from typing import List
#
# import pendulum
# from sqlalchemy import select
#
# from src.db.session import session_scope
# # from src.models.exam_category_group import ExamCategoryGroup
# from src.shared.response import Response
# from src.shared.response_code import ResponseCode
# from src.types import ExamCategoryGroupsInput, ExamCategoryGroupsNode
#
#
# class ExamCategoryGroupsService(object):
#     @staticmethod
#     def get_exam_category_groups() -> List[ExamCategoryGroup]:
#         with session_scope() as session:
#             result = session.query(
#                 ExamCategoryGroup.uid,
#                 ExamCategoryGroup.name,
#                 ExamCategoryGroup.created_at,
#                 ExamCategoryGroup.updated_at,
#             ).filter(ExamCategoryGroup.deleted_at.is_(None)).all()
#             return result
#
#     @staticmethod
#     def get_exam_category_groups_by_ids(ids: List[str]) -> List[ExamCategoryGroup]:
#         """
#         Get exam_category_groups by ids
#         :return:
#         """
#         with session_scope() as session:
#             stmt = select(ExamCategoryGroup).where(
#                 (ExamCategoryGroup.id.in_(ids)) & (ExamCategoryGroup.deleted_at.is_(None)))
#             result = session.scalars(stmt)
#             return result.all()
#
#     @staticmethod
#     def get_exam_category_groups_id(id: str) -> ExamCategoryGroup:
#         """
#         Get exam_category_groups by id
#         :param id:
#         :return:
#         """
#         with session_scope() as session:
#             stmt = select(ExamCategoryGroup).where(
#                 (ExamCategoryGroup.id == id) & (ExamCategoryGroup.deleted_at.is_(None)))
#             result = session.scalars(stmt)
#             return result.first()
#
#     @staticmethod
#     def get_exam_category_groups_by_uids(uids: List[str]) -> List[ExamCategoryGroup]:
#         """
#         Get exam_category_groups by uids
#         :param uids:
#         :return:
#         """
#         with session_scope() as session:
#             stmt = select(ExamCategoryGroup).where(
#                 (ExamCategoryGroup.uid.in_(uids)) & (ExamCategoryGroup.deleted_at.is_(None)))
#             result = session.scalars(stmt)
#             return result.all()
#
#     @staticmethod
#     def get_exam_category_groups_by_uid(uid: str) -> ExamCategoryGroup:
#         """
#         Get exam_category_groups by uid
#         :param uid:
#         :return:
#         """
#         with session_scope() as session:
#             stmt = select(ExamCategoryGroup).where(
#                 (ExamCategoryGroup.uid == uid) & (ExamCategoryGroup.deleted_at.is_(None)))
#             result = session.scalars(stmt)
#             return result.first()
#
#     def register_exam_category_groups(self, inputs: List[ExamCategoryGroupsInput]) -> Response[List[ExamCategoryGroupsNode]]:
#         """
#         Register Exam Category Group
#         :param inputs:
#         :return:
#         """
#         exam_category_groups_list = []
#         with session_scope() as session:
#             existed_exam_category_group = self.get_exam_category_groups_by_uids([item.uid for item in inputs])
#             # create new exam category group
#             for inputItem in inputs:
#                 if inputItem.uid is None:
#
#                     exam_category_groups = ExamCategoryGroup(
#                         name=inputItem.name
#                     )
#                     exam_category_groups_list.append(exam_category_groups)
#                 else:
#                     exam_category_groups = next(
#                         filter(lambda exam_category_group: str(exam_category_group.uid) == str(inputItem.uid),
#                                existed_exam_category_group), None)
#
#                     if exam_category_groups:
#                         exam_category_groups.name = inputItem.name
#                         exam_category_groups_list.append(exam_category_groups)
#             session.add_all(exam_category_groups_list)
#             session.commit()
#             return Response(status=True, code=ResponseCode.SUCCESS, data=exam_category_groups_list,
#                             message="Successfully Submitted")
#
#     @staticmethod
#     def remove_exam_category_group(uid: str):
#         """
#         Remove Exam Category Group
#         :param uid:
#         :return:
#         """
#         with session_scope() as session:
#             session.query(ExamCategoryGroup).filter_by(uid=uid).update({ExamCategoryGroup.deleted_at: pendulum.now()})
#             session.commit()
#
