from typing import Any

from talos.core.scheduled_job import ScheduledJob
from talos.database.models import Counter
from talos.database.session import get_session


class IncrementCounterJob(ScheduledJob):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            name="increment_counter",
            description="Increment the counter",
            cron_expression="* * * * *",
        )

    async def run(self, **kwargs: Any) -> Any:
        """Increment the counter."""
        print("Incrementing counter")

        with get_session() as session:
            counter = session.query(Counter).filter(Counter.name == "test").first()
            if not counter:
                counter = Counter(name="test", value=0)
                session.add(counter)
                session.commit()
                session.refresh(counter)
            counter.value += 1
            session.commit()
            return counter.value
