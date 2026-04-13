from db import Base, engine
from models import User, Reports  # make sure models are imported

Base.metadata.create_all(bind=engine)