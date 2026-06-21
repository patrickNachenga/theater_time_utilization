"""
Seed script to generate 10,000+ theatre procedure records over 1 year for analytics testing.

Run this inside the Docker container:
    docker exec -i mnh-theatre-time python3 /app/seed_analytics_data.py
"""
import random
import uuid
from datetime import datetime, timedelta, date, time

from src.database.session import session_scope
from src.models import (
    TheatreProcedureRecord,
    TheatreRecordDelay,
    TheatreRecordTeamMember,
    Procedure,
    TheatreUnit,
    Region,
    TheatreMember,
    InternalSource,
    ExternalSource,
    DeathReason,
    ProcedureDelayCause,
    ProcedureDelayCategory,
)
from src.models.theatre_procedure_record import (
    PatientOutcome,
    PatientType,
    SourceType,
    TeamRole,
    DischargeDirection,
)


# ---------- Configuration ----------
TOTAL_RECORDS = 12000
START_DATE = date(2025, 6, 1)
END_DATE = date(2026, 6, 1)

# Probability weights
P_EMERGENCY = 0.35        # 35% emergency
P_DELAY = 0.30            # 30% have delays
P_DEATH = 0.05            # 5% mortality rate
P_EXTERNAL_SOURCE = 0.40  # 40% external referrals
P_HAS_ESTIMATE = 0.85     # 85% have estimated duration

# Working hours
WORK_START_HOUR = 8   # 8 AM
WORK_END_HOUR = 17    # 5 PM

# Team roles distribution per procedure
TEAM_ROLE_DISTRIBUTION = {
    TeamRole.SURGEON: 2,        # 2 surgeons
    TeamRole.ANESTHETIST: 1,    # 1 anesthetist
    TeamRole.SCRUB_NURSE: 2,    # 2 scrub nurses
    TeamRole.RUNNER_NURSE: 1,   # 1 runner nurse
}


def random_time_in_workday():
    """Generate a random start time during working hours."""
    hour = random.randint(WORK_START_HOUR, WORK_END_HOUR - 1)
    minute = random.choice([0, 15, 30, 45])
    return time(hour, minute)


def calculate_duration(procedure_estimated_minutes):
    """Generate realistic duration based on estimated time."""
    if procedure_estimated_minutes is None:
        procedure_estimated_minutes = random.randint(30, 240)

    # Actual duration varies around estimate
    variance_factor = random.uniform(0.7, 1.5)
    actual_minutes = int(procedure_estimated_minutes * variance_factor)
    return max(15, min(600, actual_minutes)), procedure_estimated_minutes


def generate_patient_mrn(index):
    """Generate a unique patient MRN."""
    return f"MNH-{2025}-{index:06d}"


def generate_dob():
    """Generate a random date of birth (18-80 years old)."""
    age_days = random.randint(18 * 365, 80 * 365)
    return START_DATE - timedelta(days=age_days)


def get_random_date():
    """Get a random date between START_DATE and END_DATE."""
    days_range = (END_DATE - START_DATE).days
    random_days = random.randint(0, days_range - 1)
    return START_DATE + timedelta(days=random_days)


def main():
    print(f"Generating {TOTAL_RECORDS} theatre procedure records...")
    print(f"Date range: {START_DATE} to {END_DATE}")

    with session_scope() as session:
        # Load reference data
        procedures = session.query(Procedure).all()
        units = session.query(TheatreUnit).all()
        regions = session.query(Region).all()
        members = session.query(TheatreMember).all()
        int_sources = session.query(InternalSource).all()
        ext_sources = session.query(ExternalSource).all()
        death_reasons = session.query(DeathReason).all()
        delay_causes = session.query(ProcedureDelayCause).all()
        delay_categories = session.query(ProcedureDelayCategory).all()

        if not procedures or not units or not regions or not members:
            print("ERROR: Missing reference data! Ensure procedures, units, regions, and members exist.")
            return

        print(f"Reference data loaded: {len(procedures)} procedures, {len(units)} units, "
              f"{len(regions)} regions, {len(members)} members")
        print(f"  {len(int_sources)} internal sources, {len(ext_sources)} external sources")
        print(f"  {len(death_reasons)} death reasons, {len(delay_causes)} delay causes")

        # Filter out non-surgery theatre units (units 1-8 are delay categories mislabeled as units)
        surgery_units = [u for u in units if u.id > 8]
        if not surgery_units:
            surgery_units = units

        # Filter actual delay categories (categories 2-9 are real, skip id=1 "mbmbmnb")
        actual_delay_categories = [c for c in delay_categories if c.id > 1]
        if not actual_delay_categories:
            actual_delay_categories = delay_categories

        # Filter valid delay causes (id=2 only is valid)
        valid_delay_causes = [c for c in delay_causes if c.id >= 2]
        if not valid_delay_causes:
            valid_delay_causes = delay_causes

        records_created = 0
        batch_size = 500

        for batch_start in range(0, TOTAL_RECORDS, batch_size):
            batch_end = min(batch_start + batch_size, TOTAL_RECORDS)
            batch_records = []

            for i in range(batch_start, batch_end):
                # Select base data
                procedure = random.choice(procedures)
                unit = random.choice(surgery_units)
                region = random.choice(regions)
                procedure_date = get_random_date()
                start_time = random_time_in_workday()

                # Patient demographics
                patient_type = random.choices(
                    [PatientType.ELECTIVE, PatientType.EMERGENCY],
                    weights=[1 - P_EMERGENCY, P_EMERGENCY]
                )[0]

                patient_mrn = generate_patient_mrn(i)
                patient_dob = generate_dob()
                patient_sex = random.choice(["MALE", "FEMALE"])

                # Source
                source_type = random.choices(
                    [SourceType.INTERNAL, SourceType.EXTERNAL],
                    weights=[1 - P_EXTERNAL_SOURCE, P_EXTERNAL_SOURCE]
                )[0]
                internal_source = random.choice(int_sources) if int_sources else None
                external_source = random.choice(ext_sources) if ext_sources else None

                # Duration
                duration, estimated = calculate_duration(procedure.estimated_minutes)
                actual_estimated = estimated if random.random() < P_HAS_ESTIMATE else None
                variance = (duration - actual_estimated) if actual_estimated else None
                end_hour = start_time.hour + (duration // 60)
                end_minute = start_time.minute + (duration % 60)
                if end_minute >= 60:
                    end_hour += 1
                    end_minute -= 60
                end_time = time(min(23, end_hour), min(59, end_minute))

                # Delay
                had_delay = random.random() < P_DELAY
                delay_reason = None
                if had_delay and valid_delay_causes:
                    delay_cause = random.choice(valid_delay_causes)
                    delay_reason = f"Delay cause: {delay_cause.name}"

                # Outcome
                outcome = random.choices(
                    [PatientOutcome.DISCHARGED, PatientOutcome.DEATH],
                    weights=[1 - P_DEATH, P_DEATH]
                )[0]
                discharge_direction = None
                discharge_destination_id = None
                death_reason_id = None
                death_description = None

                if outcome == PatientOutcome.DISCHARGED:
                    discharge_direction = random.choice(
                        [DischargeDirection.HOME, DischargeDirection.INTERNAL]
                    )
                    if discharge_direction == DischargeDirection.INTERNAL and int_sources:
                        discharge_destination_id = random.choice(int_sources).id
                else:
                    if death_reasons:
                        dr = random.choice(death_reasons)
                        death_reason_id = dr.id
                        death_description = f"Patient expired due to {dr.name}"

                # Additional flags
                surgery_beyond_theatre_time = random.random() < 0.10 if had_delay else False
                surgery_met_time_between_cases = random.random() < 0.85
                met_turnaround_target = random.random() < 0.75

                # Create record
                record = TheatreProcedureRecord(
                    uid=uuid.uuid4(),
                    patient_mrn=patient_mrn,
                    patient_dob=patient_dob,
                    patient_sex=patient_sex,
                    patient_region_id=region.id,
                    patient_type=patient_type,
                    patient_source_type=source_type,
                    internal_source_id=internal_source.id if source_type == SourceType.INTERNAL and internal_source else None,
                    external_source_id=external_source.id if source_type == SourceType.EXTERNAL and external_source else None,
                    theatre_unit_id=unit.id,
                    procedure_id=procedure.id,
                    procedure_date=procedure_date,
                    procedure_start_time=start_time,
                    procedure_end_time=end_time,
                    duration_minutes=duration,
                    estimated_duration_minutes=actual_estimated,
                    variance_minutes=variance,
                    met_turnaround_target=met_turnaround_target,
                    had_delay=had_delay,
                    delay_reason=delay_reason,
                    surgery_beyond_theatre_time=surgery_beyond_theatre_time,
                    surgery_met_time_between_cases=surgery_met_time_between_cases,
                    outcome=outcome,
                    discharge_direction=discharge_direction,
                    discharge_destination_id=discharge_destination_id,
                    death_reason_id=death_reason_id,
                    death_description=death_description,
                    created_by=1,
                )
                session.add(record)
                session.flush()  # Get the record ID

                # Create delay record if had_delay
                if had_delay and valid_delay_causes:
                    delay_cause = random.choice(valid_delay_causes)
                    delay_record = TheatreRecordDelay(
                        record_id=record.id,
                        cause_id=delay_cause.id,
                        description=delay_reason,
                        created_by=1,
                    )
                    session.add(delay_record)

                # Create team members for this record
                assigned_roles = set()
                for role, count in TEAM_ROLE_DISTRIBUTION.items():
                    for _ in range(count):
                        member = random.choice(members)
                        team_record = TheatreRecordTeamMember(
                            record_id=record.id,
                            theatre_member_id=member.id,
                            role=role,
                            rank=random.randint(1, 5),
                            created_by=1,
                        )
                        session.add(team_record)

                records_created += 1

                if (records_created) % 1000 == 0:
                    print(f"  Created {records_created}/{TOTAL_RECORDS} records...")
                    session.flush()

            # Commit batch
            session.flush()

        print(f"\nSuccessfully created {records_created} records!")
        print(f"Total theatre procedure records: {session.query(TheatreProcedureRecord).count()}")
        print(f"Total delay records: {session.query(TheatreRecordDelay).count()}")
        print(f"Total team member records: {session.query(TheatreRecordTeamMember).count()}")


if __name__ == "__main__":
    main()