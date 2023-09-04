from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from src.core.security import Info
from src.db.session import session_scope
from src.models import TransitionMeta, Workflow, State
from src.modules import CRUDBase
from src.modules.states.service import StateService
from src.modules.workflows.service import WorkflowService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import TransitionMetaInput, PaginatedTransitionMeta


class TransitionMetaService(CRUDBase[TransitionMeta, TransitionMetaInput, TransitionMetaInput]):

    @staticmethod
    def get_transition_metas() -> List[TransitionMeta]:
        with session_scope() as session:
            result = session.query(TransitionMeta).all()
            return result

    @staticmethod
    def get_transition_metas_by_uids(ids: List[str]) -> List[TransitionMeta]:
        """
            Get Transition Metas by uids
        :return:
        """
        with session_scope() as session:
            query = session.query(TransitionMeta).filter((TransitionMeta.uid.in_(ids)))
            result = query.all()
            return result

    @staticmethod
    def get_transition_metas_by_workflow(workflow_uid: str) -> List[TransitionMeta]:
        """
            Get TransitionMeta by Workflow
        :param workflow_uid:
        :return:
        """
        with session_scope() as session:
            workflow = WorkflowService(Workflow).get(uid=workflow_uid)
            return session.query(TransitionMeta).options(joinedload(TransitionMeta.source_state),
                                                         joinedload(TransitionMeta.destination_state)).filter(
                TransitionMeta.workflow == workflow).all()

    def register_transition_metas(self, inputs: List[TransitionMetaInput], info: Info) -> (
            Response)[PaginatedTransitionMeta]:
        """
        Register Transition Metas
        :param inputs:
        :param info:
        :return:
        """
        transition_meta_list = []
        with session_scope() as session:
            count = session.query(TransitionMeta).count()
            # check for existing Transitions using uid
            existed_transition_metas = self.get_transition_metas_by_uids([input.uid for input in inputs])

            # create new TransitionMeta
            for input1 in inputs:
                workflow = WorkflowService(Workflow).get(input1.workflow_uid)
                source_state = StateService(State).get(input1.source_state_uid)
                destination_state = StateService(State).get(input1.destination_state_uid)

                if not workflow:
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                    data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                    message="Workflow Does not Exists")
                if not source_state:
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                    data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                    message="Source State Does not Exists")
                if not destination_state:
                    return Response(status=False, code=ResponseCode.NO_RECORD_FOUND,
                                    data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                    message="Destination State Does not Exists")

                if source_state == destination_state:
                    return Response(status=False, code=ResponseCode.BAD_REQUEST,
                                    data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                    message="Source state and destination state cannot be the same")

                if input1.is_first and input1.is_last:
                    return Response(status=False, code=ResponseCode.BAD_REQUEST,
                                    data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                    message="Transition cannot be the First and Last State")

                existing_transition_meta = session.query(TransitionMeta).filter(
                    and_(
                        TransitionMeta.source_state_id == source_state.id,
                        TransitionMeta.destination_state_id == destination_state.id,
                        TransitionMeta.deleted_at == None
                    )
                ).first()

                if existing_transition_meta is not None and input1.uid is None:
                    return Response(status=False, code=ResponseCode.BAD_REQUEST,
                                    data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                    message="A record with the same source state and destination state "
                                            "already exists")

                if not input1.groups:
                    input1.groups = []
                if not input1.permissions:
                    input1.permissions = []
                if input1.uid is None:
                    if input1.is_first:
                        # mark False is_first for all on that workflow
                        pass
                    if input1.is_last:
                        # mark False is_last for all on that workflow
                        pass
                    transition_meta = TransitionMeta(workflow=workflow, source_state=source_state,
                                                     destination_state=destination_state,
                                                     created_by=info.context.user.profile.id, groups=input1.groups,
                                                     is_first=input1.is_first if input1.is_first is not None else False,
                                                     is_last=input1.is_last if input1.is_last is not None else False,
                                                     permissions=input1.permissions)
                    session.add(transition_meta)
                    session.commit()
                    transition_meta_list.append(transition_meta)
                else:

                    transition_meta = next(filter(lambda transition_meta: str(transition_meta.uid) == str(input1.uid),
                                                  existed_transition_metas), None)
                    if transition_meta:
                        if existing_transition_meta is not None and transition_meta.id != existing_transition_meta.id:
                            return Response(status=False, code=ResponseCode.BAD_REQUEST,
                                            data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                                            message="A record with the same source state and destination state "
                                                    "already exists")
                        transition_meta.workflow = workflow
                        transition_meta.source_state = source_state
                        transition_meta.destination_state = destination_state
                        transition_meta.groups = input1.groups
                        transition_meta.permissions = input1.permissions
                        if input1.is_first is not None:
                            transition_meta.is_first = input1.is_first
                        if input1.is_last is not None:
                            transition_meta.is_last = input1.is_last
                        session.merge(transition_meta)
                        session.commit()
                        transition_meta_list.append(transition_meta)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=PaginatedTransitionMeta(items=transition_meta_list, total_count=count),
                            message="Successfully Submitted")


TransitionMetaCrud = TransitionMetaService(TransitionMeta)
