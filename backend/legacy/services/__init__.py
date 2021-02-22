try:
    from ..db import get_session
except:
    from db import get_session



class BaseService(object):
    model = None

    def __init__(self):
        self.session = get_session()

    def all(self):
        return self.session.query(self.model).all()

    def save(self, model):
        self.session.add(model)
        self.session.commit()

    def refresh(self, model):
        self.session.refresh(model)

    def get(self, pk):
        return self.session.query(self.model).filter(self.model.id == pk).first()

    def delete(self, model):
        if isinstance(model, int):
            model = self.get(model)
        for cs in model.cascade():
            self.delete(cs)
        self.session.delete(model)
        self.session.commit()
