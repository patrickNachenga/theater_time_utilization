import strawberry

from src.modules.procedure_delay_category.apis import ProcedureDelayCategoryQuery, ProcedureDelayCategoryMutation
from src.modules.procedure_delay_cause.apis import ProcedureDelayCauseQuery, ProcedureDelayCauseMutation
from src.modules.procedure.apis import ProcedureQuery, ProcedureMutation
from src.modules.theatre_role.apis import TheatreRoleQuery, TheatreRoleMutation
from src.modules.theatre_member.apis import TheatreMemberQuery, TheatreMemberMutation
from src.modules.theatre_member_role.apis import TheatreMemberRoleQuery, TheatreMemberRoleMutation
from src.modules.region.apis import RegionQuery, RegionMutation
from src.modules.internal_source.apis import InternalSourceQuery, InternalSourceMutation
from src.modules.external_source.apis import ExternalSourceQuery, ExternalSourceMutation
from src.modules.theatre_unit.apis import TheatreUnitQuery, TheatreUnitMutation
from src.modules.death_reason.apis import DeathReasonQuery, DeathReasonMutation
from src.modules.theatre_time_record.apis import TheatreTimeRecordQuery, TheatreTimeRecordMutation
from src.modules.theatre_record_team_member.apis import TheatreRecordTeamMemberQuery, TheatreRecordTeamMemberMutation
from src.modules.theatre_record_delay.apis import TheatreRecordDelayQuery, TheatreRecordDelayMutation



@strawberry.type
class ApiQuery(ProcedureDelayCategoryQuery,
               ProcedureDelayCauseQuery,
               ProcedureQuery,
               TheatreRoleQuery,
               TheatreMemberQuery,
               TheatreMemberRoleQuery,
               RegionQuery,
               InternalSourceQuery,
               ExternalSourceQuery,
               TheatreUnitQuery,
               DeathReasonQuery,
               TheatreTimeRecordQuery,
               TheatreRecordTeamMemberQuery,
               TheatreRecordDelayQuery,
               ):
    pass


@strawberry.type
class ApiMutation(ProcedureDelayCategoryMutation,
                  ProcedureDelayCauseMutation,
                  ProcedureMutation,
                  TheatreRoleMutation,
                  TheatreMemberMutation,
                  TheatreMemberRoleMutation,
                  RegionMutation,
                  InternalSourceMutation,
                  ExternalSourceMutation,
                  TheatreUnitMutation,
                  DeathReasonMutation,
                  TheatreTimeRecordMutation,
                  TheatreRecordTeamMemberMutation,
                  TheatreRecordDelayMutation,
                  ):
    pass
