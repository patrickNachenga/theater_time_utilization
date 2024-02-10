from typing import List

from src.core.security import Info
from src.db.session import session_scope
from src.models import Workflow
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import WorkflowInput, PaginatedWorkflow


class WorkflowService(CRUDBase[Workflow, WorkflowInput, WorkflowInput]):

    @staticmethod
    def get_workflows() -> List[Workflow]:
        with session_scope() as session:
            result = session.query(Workflow).all()
            return result

    @staticmethod
    def get_workflows_by_uids(ids: List[str]) -> List[Workflow]:
        """
            Get Workflows by uids
        :return:
        """
        with session_scope() as session:
            query = session.query(Workflow).filter((Workflow.uid.in_(ids)))
            result = query.all()
            return result

    @staticmethod
    def get_workflows_by_names(names: List[str]) -> List[Workflow]:
        """
            Get Workflows by names
        :return:
        """
        with session_scope() as session:
            query = session.query(Workflow).filter((Workflow.name.in_(names)))
            result = query.all()
            return result

    @staticmethod
    def get_workflow_by_name(name: str) -> Workflow:
        """
            Get Workflow by name
        :param name:
        :return:
        """
        with session_scope() as session:
            query = session.query(Workflow).filter((Workflow.name == name))
            result = query.first()
            return result

    def register_workflows(self, inputs: List[WorkflowInput], info: Info) -> Response[PaginatedWorkflow]:
        """
        Register Workflows
        :param inputs:
        :param info:
        :return:
        """
        workflow_list = []
        with session_scope() as session:
            count = session.query(Workflow).count()
            # Check if Workflow already exist using code or name

            existed_workflow_by_name_list = self.get_workflows_by_names(
                [workflow.name for workflow in inputs if workflow.uid is None])
            if existed_workflow_by_name_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=PaginatedWorkflow(items=workflow_list, total_count=count),
                                message="Workflow Already exist")
            # check for existing Workflows using uid
            existed_workflows = self.get_workflows_by_uids([input.uid for input in inputs])

            # create new workflows
            for input1 in inputs:
                if input1.uid is None:
                    workflow = Workflow(name=input1.name, description=input1.description,
                                        created_by=info.context.user.id)
                    session.add(workflow)
                    session.commit()
                    workflow_list.append(workflow)
                else:
                    workflow = next(filter(lambda workflow: str(workflow.uid) == str(input1.uid),
                                           existed_workflows), None)
                    if workflow:
                        workflow.name = input1.name
                        workflow.description = input1.description
                        session.merge(workflow)
                        session.commit()
                        workflow_list.append(workflow)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=PaginatedWorkflow(items=workflow_list, total_count=count),
                            message="Successfully Submitted")


WorkflowCrud = WorkflowService(Workflow)
