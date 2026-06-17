from .service import get_groups, get_jobs


def jobs_handl(group_id: int, jobs: list[tuple]) -> None:
    ...

def start_loop() -> None:
    for group in get_groups():
        jobs_handl(group_id=group, jobs=get_jobs(group))