from typing import List

from src.core.security import Info
from src.db.session import session_scope
from src.models import State
from src.modules import CRUDBase
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import StateInput, PaginatedState


class StateService(CRUDBase[State, StateInput, StateInput]):

    @staticmethod
    def get_states() -> List[State]:
        with session_scope() as session:
            result = session.query(State).all()
            return result

    @staticmethod
    def get_states_by_uids(ids: List[str]) -> List[State]:
        """
            Get States by uids
        :return:
        """
        with session_scope() as session:
            query = session.query(State).filter((State.uid.in_(ids)))
            result = query.all()
            return result

    @staticmethod
    def get_states_by_labels(labels: List[str]) -> List[State]:
        """
            Get States by labels
        :return:
        """
        with session_scope() as session:
            query = session.query(State).filter((State.label.in_(labels)))
            result = query.all()
            return result

    @staticmethod
    def get_state_by_label(label: str) -> State:
        """
            Get State by label
        :param label:
        :return:
        """
        with session_scope() as session:
            query = session.query(State).filter((State.label == label))
            result = query.first()
            return result

    def register_states(self, inputs: List[StateInput], info: Info) -> Response[PaginatedState]:
        """
        Register States
        :param inputs:
        :param info:
        :return:
        """
        state_list = []
        with session_scope() as session:
            count = session.query(State).count()
            # Check if State already exist using label

            existed_state_by_label_list = self.get_states_by_labels(
                [state.label for state in inputs if state.uid is None])
            if existed_state_by_label_list:
                return Response(status=False, code=ResponseCode.DUPLICATE,
                                data=PaginatedState(items=state_list, total_count=count),
                                message="State Already exist")
            # check for existing States using uid
            existed_states = self.get_states_by_uids([input.uid for input in inputs])

            # create new state
            for input1 in inputs:
                if input1.uid is None:
                    state = State(label=input1.label, description=input1.description,
                                  created_by=info.context.user.profile.id)
                    session.add(state)
                    session.commit()
                    state_list.append(state)
                else:
                    state = next(filter(lambda state: str(state.uid) == str(input1.uid),
                                        existed_states), None)
                    if state:
                        state.label = input1.label
                        state.description = input1.description
                        session.merge(state)
                        session.commit()
                        state_list.append(state)
            return Response(status=True, code=ResponseCode.SUCCESS,
                            data=PaginatedState(items=state_list, total_count=count),
                            message="Successfully Submitted")


StateCrud = StateService(State)
