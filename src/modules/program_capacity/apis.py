import strawberry

from src.modules.program_capacity.service import ProgramCapacityService
from src.shared.response import Response
from src.shared.response_code import ResponseCode
from src.types import ProgramCapacityNode, ProgramCapacityListNode, \
    ProgramCapacityInputNode


@strawberry.type
class ProgramCapacityQuery:
    @strawberry.field
    def get_program_program_capacity(self, program_uid: str) -> Response[ProgramCapacityNode]:
        try:
            result = ProgramCapacityService().get_program_capacity(program_uid)
        except Exception as e:
            print(e)
            result = []
        if result:
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program capacity Retrieved successfully",
                data=result)
        else:
            return Response(
                status=False,
                code=ResponseCode.NO_RECORD_FOUND,
                message="Program not found",
                data=result)


@strawberry.type
class ProgramCapacityMutation:

    @strawberry.field
    def register_program_capacity(self, inputs: ProgramCapacityInputNode) -> Response[ProgramCapacityListNode]:
        try:
            return ProgramCapacityService().register_program_capacity(inputs)

        except Exception as e:
            print(e)
            return Response(status=False, code=ResponseCode.FAILURE, message="Failed to register program capacity",
                            data=[])

    # delete program capacity
    @strawberry.mutation
    async def remove_program(self, uid: str) -> Response[ProgramCapacityListNode]:
        """
        Remove student By UID
        :param uid:
        :return:
        """
        try:
            results = ProgramCapacityService.remove_program_capacity(uid)
            return Response(
                status=True,
                code=ResponseCode.SUCCESS,
                message="Program Capacity Removed Successfully",
                data=results
            )
        except Exception as e:
            print(e)
            return Response(
                status=False,
                code=ResponseCode.FAILURE,
                message="Failed to Remove Program capacity",
                data=ProgramCapacityListNode(items=[], total_count=0)
            )
