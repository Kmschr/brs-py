import pytest
import uuid
from datetime import datetime, timezone
from brs.brs import BRS, Brick
from brs.user import User, BrickOwner
from brs.color import Color, ColorMode
from brs.orientation import Direction, Rotation

@pytest.fixture
def empty_save():
    save = BRS()
    save.version = 8
    save.game_version = 6094
    save.author = User("Tester", uuid.uuid4())
    save.host = save.author
    save.time = datetime.now(timezone.utc)
    return save

@pytest.fixture
def default_brick():
    return Brick.default()

@pytest.fixture
def sample_user():
    return User("TestUser", uuid.uuid4())
